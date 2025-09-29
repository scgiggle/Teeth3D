<template>
  <div>
    <canvas ref="canvasRef"></canvas>
  </div>
</template>

<script setup>
import { onMounted, ref, watch, nextTick } from 'vue'

const props = defineProps({
  imageUrl: { type: String, required: true },
  maskOpacity: { type: Number, default: 0.5 },
})

const canvasRef = ref(null)

async function draw() {
  await nextTick()
  const canvas = canvasRef.value
  if (!canvas) return
  const ctx = canvas.getContext('2d')
  const img = new Image()
  img.crossOrigin = 'anonymous'
  img.onload = () => {
    canvas.width = img.width
    canvas.height = img.height
    ctx.drawImage(img, 0, 0)
    // 占位：这里可叠加分割掩码
    ctx.fillStyle = `rgba(0, 150, 255, ${props.maskOpacity})`
    ctx.fillRect(0, 0, canvas.width, canvas.height)
  }
  img.src = props.imageUrl
}

onMounted(draw)
watch(() => [props.imageUrl, props.maskOpacity], draw)
</script>


