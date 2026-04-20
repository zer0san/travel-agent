import axios from 'axios'

const api = axios.create({
    baseURL: 'http://localhost:8080/api', // Replace with your API base URL
    timeout: 180000,
    headers: {
        'Content-Type': 'application/json',
    },
    withCredentials: true
})

export async function generateTripPlan(data){
    try{
        const response = await api.post('/generate-trip-plan', data)
        return response.data
    } catch (error) {
        console.log("生成计划失败:", error)
        throw error
    }
}

export async function getAttractionPhotos(name) {
    try {
        const response = await api.get('/get_attraction_photos', {
            params: { name }
        })
        return Array.isArray(response.data) ? response.data : []
    } catch (error) {
        console.log('获取景点图片失败:', error)
        throw error
    }
}

