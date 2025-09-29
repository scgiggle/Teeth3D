<template>
  <div ref="containerRef" style="width:100%;height:60vh;"></div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import * as THREE from 'three'

const props = defineProps({
  modelUrl: { type: String, default: '' },
})

const containerRef = ref(null)

onMounted(() => {
  const container = containerRef.value
  const scene = new THREE.Scene()
  const camera = new THREE.PerspectiveCamera(60, container.clientWidth / container.clientHeight, 0.1, 1000)
  camera.position.z = 5

  const renderer = new THREE.WebGLRenderer({ antialias: true })
  renderer.setSize(container.clientWidth, container.clientHeight)
  container.appendChild(renderer.domElement)

  const light = new THREE.DirectionalLight(0xffffff, 1)
  light.position.set(1, 1, 1)
  scene.add(light)

  const geometry = new THREE.BoxGeometry(1, 1, 1)
  const material = new THREE.MeshStandardMaterial({ color: 0x409eff })
  const cube = new THREE.Mesh(geometry, material)
  scene.add(cube)

  const animate = () => {
    requestAnimationFrame(animate)
    cube.rotation.x += 0.005
    cube.rotation.y += 0.01
    renderer.render(scene, camera)
  }
  animate()
})
</script>


