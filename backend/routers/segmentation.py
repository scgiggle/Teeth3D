from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
import uuid
import redis
from typing import Optional
import numpy as np
import torch
from PIL import Image
import io
import base64
import os

from database import get_redis
from routers.auth import get_current_user, User

router = APIRouter()

import threading

# Module-level cache for SAM2 model and predictor class
_SAM2_MODEL = None
_SAM2_PREDICTOR_CLASS = None
_SAM2_DEVICE = None
_SAM2_LOCK = threading.Lock()


def get_sam2_model_and_predictor():
    """Return (sam2_model, SAM2ImagePredictorClass, device).
    Initialize and cache the SAM2 model on first call in a thread-safe way.
    """
    global _SAM2_MODEL, _SAM2_PREDICTOR_CLASS, _SAM2_DEVICE
    if _SAM2_MODEL is None:
        with _SAM2_LOCK:
            if _SAM2_MODEL is None:
                # choose device
                if torch.cuda.is_available():
                    _SAM2_DEVICE = torch.device("cuda")
                else:
                    _SAM2_DEVICE = torch.device("cpu")

                model_cfg = "configs/sam2.1/sam2.1_hiera_l.yaml"
                base_dir = os.path.dirname(os.path.abspath(__file__))
                sam2_checkpoint = os.path.join(base_dir, "../checkpoints/sam2.1_hiera_large.pt")

                try:
                    from sam2.build_sam import build_sam2
                    from sam2.sam2_image_predictor import SAM2ImagePredictor
                except Exception as e:
                    raise RuntimeError(f"Failed to import SAM2 modules: {e}")

                try:
                    _SAM2_MODEL = build_sam2(model_cfg, sam2_checkpoint, device=_SAM2_DEVICE)
                except Exception as e:
                    raise RuntimeError(f"Error building SAM2 model: {e}")

                _SAM2_PREDICTOR_CLASS = SAM2ImagePredictor
    return _SAM2_MODEL, _SAM2_PREDICTOR_CLASS, _SAM2_DEVICE


class SegmentationResult(BaseModel):
    image_id: str
    status: str
    result_url: Optional[str] = None

@router.post("/upload")
async def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    redis_client: redis.Redis = Depends(get_redis)
):
    """上传图像进行分割"""
    if not redis_client:
        raise HTTPException(status_code=500, detail="Redis connection failed")
    
    # 验证文件类型
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="只支持图像文件")
    
    # 生成图像ID
    image_id = str(uuid.uuid4())
    
    # 这里应该保存文件到磁盘或云存储
    # 暂时只存储元数据
    image_info = {
        "image_id": image_id,
        "filename": file.filename,
        "content_type": file.content_type,
        "user": current_user.username,
        "status": "uploaded",
        "created_at": "2024-01-01T00:00:00"
    }
    
    redis_client.hset(f"image:{image_id}", mapping=image_info)
    
    return {"image_id": image_id, "message": "图像上传成功"}


@router.get("/{image_id}")
async def get_segmentation_result(
    image_id: str,
    current_user: User = Depends(get_current_user),
    redis_client: redis.Redis = Depends(get_redis)
):
    """获取分割结果"""
    if not redis_client:
        raise HTTPException(status_code=500, detail="Redis connection failed")

    image_info = redis_client.hgetall(f"image:{image_id}")
    if not image_info:
        raise HTTPException(status_code=404, detail="图像不存在")

    # Redis 返回 bytes -> 解码为 str
    def _decode(v):
        if isinstance(v, bytes):
            return v.decode()
        return v

    image_info_decoded = { (k.decode() if isinstance(k, bytes) else k): _decode(v) for k, v in image_info.items() }

    # 检查用户权限
    if image_info_decoded.get("user") != current_user.username:
        raise HTTPException(status_code=403, detail="无权限访问")

    return SegmentationResult(
        image_id=image_id,
        status=image_info_decoded.get("status", "unknown"),
        result_url=image_info_decoded.get("result_url")
    )

@router.post("/{image_id}/reconstruct")
async def request_reconstruction(
    image_id: str,
    current_user: User = Depends(get_current_user),
    redis_client: redis.Redis = Depends(get_redis)
):
    """请求3D重建"""
    if not redis_client:
        raise HTTPException(status_code=500, detail="Redis connection failed")
    
    image_info = redis_client.hgetall(f"image:{image_id}")
    if not image_info:
        raise HTTPException(status_code=404, detail="图像不存在")
    
    # 检查用户权限
    if image_info["user"] != current_user.username:
        raise HTTPException(status_code=403, detail="无权限访问")
    
    # 更新状态为重建中
    redis_client.hset(f"image:{image_id}", "status", "reconstructing")
    
    # 生成模型ID
    model_id = str(uuid.uuid4())
    redis_client.hset(f"model:{model_id}", mapping={
        "model_id": model_id,
        "image_id": image_id,
        "user": current_user.username,
        "status": "processing",
        "created_at": "2024-01-01T00:00:00"
    })
    
    return {"model_id": model_id, "message": "3D重建请求已提交"}

def show_mask(mask, ax, random_color=False, borders=True):
    color = np.array([30/255, 144/255, 255/255]) 
    h, w = mask.shape[-2:]
    mask = mask.astype(np.uint8)
    mask_image = mask.reshape(h, w, 1) * color.reshape(1, 1, -1)
    if borders:
        import cv2
        contours, _ = cv2.findContours(mask,cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE) 
        # Try to smooth contours
        contours = [cv2.approxPolyDP(contour, epsilon=0.01, closed=True) for contour in contours]
        mask_image = cv2.drawContours(mask_image, contours, -1, (1, 1, 1, 0.5), thickness=2)
    ax.imshow(mask_image)
    

def show_masks(image, masks, scores, point_coords=None, box_coords=None, input_labels=None, borders=True):
    # plotting removed; use start_to_segment for overlay generation
    for i, (mask, score) in enumerate(zip(masks, scores)):
        pass



def show_points(coords, labels, ax, marker_size=375):
    pos_points = coords[labels == 1]
    neg_points = coords[labels == 0]
    ax.scatter(pos_points[:, 0], pos_points[:, 1], color="green", marker="*", s=marker_size, edgecolor="white", linewidth=1.25)
    ax.scatter(neg_points[:, 0], neg_points[:, 1], color="red", marker="*", s=marker_size, edgecolor="white", linewidth=1.25)


def start_to_segment1(image: np.ndarray, point_coords: Optional[np.ndarray] = None, point_labels: Optional[np.ndarray] = None):
    """Run SAM2 predictor on a provided numpy RGB image and return overlay PNG as base64 string.

    Inputs:
      - image: HxWx3 uint8 numpy array (RGB)
      - point_coords: optional array shape (N,2)
      - point_labels: optional array shape (N,)

    Returns: dict {"overlay_base64": "data:image/png;base64,...", "mask_index": int}
    """
    sam2_model, SAM2ImagePredictor, device = get_sam2_model_and_predictor()

    print(f"using device: {device.type}")

    # build model
    try:
        predictor = SAM2ImagePredictor(sam2_model)
    except Exception as e:
        print(e)
        raise RuntimeError(f"Failed to import SAM2 modules: {e}")


    predictor.set_image(image)

    # default point if none provided: center of image
    if point_coords is None or point_labels is None:
        h, w = image.shape[:2]
        point_coords = np.array([[w // 2, h // 2]])
        point_labels = np.array([1])

    # ensure correct shapes
    point_coords = np.asarray(point_coords).astype(np.float32)
    point_labels = np.asarray(point_labels).astype(np.int32)

    masks, scores, logits = predictor.predict(
        point_coords=point_coords,
        point_labels=point_labels,
        multimask_output=True,
    )

    if masks is None or len(masks) == 0:
        raise RuntimeError("No masks returned by predictor")

    sorted_ind = np.argsort(scores)[::-1]
    masks = masks[sorted_ind]
    scores = scores[sorted_ind]

    best_mask = masks[0]

    # create overlay png
    color = (30, 144, 255)
    alpha = 128
    overlay = np.zeros((image.shape[0], image.shape[1], 4), dtype=np.uint8)
    overlay[..., 0] = color[0]
    overlay[..., 1] = color[1]
    overlay[..., 2] = color[2]
    overlay[..., 3] = (best_mask.astype(np.uint8) * alpha)

    orig = Image.fromarray(image).convert("RGBA")
    overlay_img = Image.fromarray(overlay, mode="RGBA")
    composed = Image.alpha_composite(orig, overlay_img)

    buf = io.BytesIO()
    composed.save(buf, format="PNG")
    buf.seek(0)
    b64 = base64.b64encode(buf.read()).decode("ascii")
    data_url = f"data:image/png;base64,{b64}"

    return {"overlay_base64": data_url, "mask_index": int(sorted_ind[0])}

def start_to_segment2(image: np.ndarray, point_coords: Optional[np.ndarray] = None, point_labels: Optional[np.ndarray] = None):
    """
    与 quick_start.py 一致，返回带分割 mask 和点击点的图片（base64）。
    使用 PIL 进行像素级合成（避免 matplotlib 在无显示环境下报错），确保只有 mask 区域被染色，其他区域保持原样，并绘制点击点。
    """
    sam2_model, SAM2ImagePredictor, device = get_sam2_model_and_predictor()
    print(f"using device: {device.type}")

    predictor = SAM2ImagePredictor(sam2_model)
    predictor.set_image(image)

    # default point if none provided: center of image
    if point_coords is None or point_labels is None:
        h, w = image.shape[:2]
        point_coords = np.array([[w // 2, h // 2]])
        point_labels = np.array([1])

    point_coords = np.asarray(point_coords).astype(np.float32)
    point_labels = np.asarray(point_labels).astype(np.int32)

    masks, scores, logits = predictor.predict(
        point_coords=point_coords,
        point_labels=point_labels,
        multimask_output=True,
    )

    if masks is None or len(masks) == 0:
        raise RuntimeError("No masks returned by predictor")

    sorted_ind = np.argsort(scores)[::-1]
    masks = masks[sorted_ind]
    scores = scores[sorted_ind]
    best_mask = masks[0]

    # 使用 PIL 进行合成：只有 mask 区域染色，其他区域保持原样；并绘制点击点
    import io, base64
    from PIL import ImageDraw

    h, w = image.shape[:2]
    # ensure image is uint8 RGB
    if image.dtype != np.uint8:
        image_uint8 = (np.clip(image, 0, 255)).astype(np.uint8)
    else:
        image_uint8 = image

    orig = Image.fromarray(image_uint8).convert("RGBA")

    # color and alpha for overlay
    overlay_color = (30, 144, 255) 
    alpha_val = int(255 * 0.6)  # 60% opacity

    # build overlay RGBA where only mask pixels have color+alpha
    overlay = np.zeros((h, w, 4), dtype=np.uint8)
    mask_bool = best_mask.astype(bool)
    overlay[..., 0][mask_bool] = overlay_color[0]
    overlay[..., 1][mask_bool] = overlay_color[1]
    overlay[..., 2][mask_bool] = overlay_color[2]
    overlay[..., 3][mask_bool] = alpha_val

    overlay_img = Image.fromarray(overlay, mode="RGBA")
    composed = Image.alpha_composite(orig, overlay_img)

    # draw points on composed image
    draw = ImageDraw.Draw(composed)
    for (xy, label) in zip(point_coords, point_labels):
        # xy is [x, y]
        x = int(round(xy[0]))
        y = int(round(xy[1]))
        r = max(4, round(min(h, w) * 0.01))
        pt_color = (0, 255, 0) if int(label) == 1 else (255, 0, 0)
        # outer white border
        draw.ellipse((x - r - 1, y - r - 1, x + r + 1, y + r + 1), fill=(255, 255, 255))
        draw.ellipse((x - r, y - r, x + r, y + r), fill=pt_color)

    buf = io.BytesIO()
    composed.save(buf, format='PNG')
    overlay_base64 = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()
    return {"overlay_base64": overlay_base64, "mask_index": int(sorted_ind[0])}

@router.post('/predict')
async def segmentation_predict(
    file: UploadFile = File(...),
    point_coords: Optional[str] = Form(None),
    point_labels: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user)):
    """接收上传图像并返回带 mask 的图片（base64 数据 URL）。

    - file: 上传的图像文件
    - point_coords: 可选，JSON 字符串，如 "[[x,y]]"
    - point_labels: 可选，JSON 字符串，如 "[1]"
    """
    # 读取并校验图片
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="只支持图像文件")

    contents = await file.read()
    try:
        pil = Image.open(io.BytesIO(contents)).convert("RGB")
    except Exception:
        raise HTTPException(status_code=400, detail="无法解析上传的图像")

    image = np.array(pil)

    # parse optional points
    import json
    pc = None
    pl = None
    if point_coords:
        try:
            pc = np.asarray(json.loads(point_coords))
        except Exception:
            raise HTTPException(status_code=400, detail="point_coords 格式错误，应为 JSON 数组")
    if point_labels:
        try:
            pl = np.asarray(json.loads(point_labels))
        except Exception:
            raise HTTPException(status_code=400, detail="point_labels 格式错误，应为 JSON 数组")

    try:
        result = start_to_segment2(image, point_coords=pc, point_labels=pl)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分割失败: {e}")

    return {"image_base64": result["overlay_base64"], "mask_index": result.get("mask_index", 0)}

