import request from '@/api/request.js'

// 上传单张图片到后端 /upload/image
export function uploadImage(filePath) {
  return request.upload(filePath, '/upload/image')
}

// 批量上传图片
export async function uploadImages(filePaths) {
  const results = []
  for (const filePath of filePaths) {
    try {
      const url = await uploadImage(filePath)
      results.push(url)
    } catch (error) {
      console.error('上传图片失败:', error)
    }
  }
  return results
}

// 删除图片 (OSS deletion not implemented in backend yet)
export function deleteImage(fileUrl) {
  return Promise.resolve(true)
}
