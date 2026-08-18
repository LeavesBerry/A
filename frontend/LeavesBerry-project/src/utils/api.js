import axios from 'axios'

export const api = axios.create({
    timeout: 5000,
    withCredentials: true
})

export const refreshApi = axios.create({
    timeout: 5000,
    withCredentials: true
})

export default api
