<template>
  <view class="uploader">
    <view class="photo-list">
      <view 
        v-for="(photo, index) in photos" 
        :key="index" 
        class="photo-item"
      >
        <image 
          :src="photo" 
          class="photo-thumb" 
          mode="aspectFill"
          @click="previewImage(index)"
        />
        <view class="photo-delete" @click="deletePhoto(index)">
          <text class="delete-icon">×</text>
        </view>
      </view>
      
      <view v-if="photos.length < maxCount" class="photo-add" @click="chooseImage">
        <text class="add-icon">+</text>
        <text class="add-text">添加照片</text>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, watch } from 'vue'
import { uploadImage } from '@/utils/oss.js'

const props = defineProps({
  modelValue: {
    type: Array,
    default: () => []
  },
  maxCount: {
    type: Number,
    default: 9
  }
})

const emit = defineEmits(['update:modelValue'])

const photos = ref([...props.modelValue])

// Only sync from external changes (parent → child)
watch(() => props.modelValue, (val) => {
  if (JSON.stringify(val) !== JSON.stringify(photos.value)) {
    photos.value = [...(val || [])]
  }
})

// Only emit when user explicitly adds/deletes (NOT from external sync)
function addPhoto(url) {
  photos.value.push(url)
  emit('update:modelValue', [...photos.value])
}
function removePhoto(index) {
  photos.value.splice(index, 1)
  emit('update:modelValue', [...photos.value])
}

const chooseImage = () => {
  const count = props.maxCount - photos.value.length
  if (count <= 0) {
    uni.showToast({ title: '已达到最大数量', icon: 'none' })
    return
  }

  uni.chooseImage({
    count: count,
    sizeType: ['compressed'],
    sourceType: ['album', 'camera'],
    success: async (res) => {
      uni.showLoading({ title: '上传中...' })
      try {
        for (const tempFilePath of res.tempFilePaths) {
          const url = await uploadImage(tempFilePath)
          addPhoto(url)
        }
        uni.hideLoading()
        uni.showToast({ title: '上传成功', icon: 'success' })
      } catch (error) {
        console.error('上传图片失败:', error)
        uni.hideLoading()
        uni.showToast({ title: '上传失败', icon: 'none' })
      }
    }
  })
}

const deletePhoto = (index) => {
  uni.showModal({
    title: '确认删除',
    content: '确定要删除该照片吗？',
    success: (res) => {
      if (res.confirm) {
        removePhoto(index)
      }
    }
  })
}

const previewImage = (current) => {
  uni.previewImage({
    urls: photos.value,
    current
  })
}
</script>

<style scoped>
.uploader {
  width: 100%;
}

.photo-list {
  display: flex;
  flex-wrap: wrap;
  gap: 16rpx;
}

.photo-item {
  position: relative;
  width: 160rpx;
  height: 160rpx;
  border-radius: 4rpx;
  overflow: hidden;
}

.photo-thumb {
  width: 100%;
  height: 100%;
}

.photo-delete {
  position: absolute;
  top: 0;
  right: 0;
  width: 40rpx;
  height: 40rpx;
  background-color: rgba(0, 0, 0, 0.6);
  border-radius: 0 8rpx 0 8rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.delete-icon {
  font-size: 28rpx;
  color: #ffffff;
  line-height: 1;
}

.photo-add {
  width: 160rpx;
  height: 160rpx;
  border: 2rpx dashed #D5DAE0;
  border-radius: 4rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background-color: #F5F7FA;
}

.add-icon {
  font-size: 48rpx;
  color: #626F7D;
  line-height: 1;
}

.add-text {
  font-size: 22rpx;
  color: #626F7D;
  margin-top: 8rpx;
}
</style>
