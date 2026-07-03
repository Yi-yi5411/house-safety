/**
 * AMap (高德地图) geocoding utility for location auto-fill.
 * Uses uni.getLocation to obtain coordinates, then reverse-geocodes via AMap API.
 */

const AMAP_KEY = '' // Set your AMap Web Service key here

/**
 * Get current location and reverse-geocode to address components.
 * Returns: { address, street, community, latitude, longitude } or null
 */
export async function getCurrentLocationAddress() {
  try {
    // Get coordinates
    const location = await new Promise((resolve, reject) => {
      uni.getLocation({
        type: 'gcj02',
        success: resolve,
        fail: reject
      })
    })

    const { latitude, longitude } = location

    if (!AMAP_KEY) {
      // Return coordinates without reverse geocoding
      return {
        address: `${longitude.toFixed(6)}, ${latitude.toFixed(6)}`,
        street: '',
        community: '',
        latitude,
        longitude
      }
    }

    // Reverse geocode via AMap
    const result = await new Promise((resolve, reject) => {
      uni.request({
        url: 'https://restapi.amap.com/v3/geocode/regeo',
        data: {
          key: AMAP_KEY,
          location: `${longitude},${latitude}`,
          extensions: 'base'
        },
        success: (res) => resolve(res.data),
        fail: reject
      })
    })

    if (result.status === '1' && result.regeocode) {
      const addr = result.regeocode.addressComponent || {}
      return {
        address: result.regeocode.formatted_address || '',
        street: addr.streetNumber
          ? `${addr.street || ''}${addr.streetNumber || ''}`
          : (addr.township || ''),
        community: addr.neighborhood?.name || addr.building?.name || '',
        latitude,
        longitude
      }
    }

    return {
      address: `${longitude.toFixed(6)}, ${latitude.toFixed(6)}`,
      street: '',
      community: '',
      latitude,
      longitude
    }
  } catch (e) {
    console.error('Location/geocode failed:', e)
    return null
  }
}
