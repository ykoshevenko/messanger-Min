import axios from 'axios'

export default class Auth {
    private username: string
    private password: string
    
    constructor(username: string, password: string){
        this.username = username
        this.password = password
    }

    async Auth() {
        try {
            const resp = await axios.post('http://127.0.0.1:8001/api/auth', {
                username: this.username,
                password: this.password
            })

            if(resp.data.access_token) {
                document.cookie = `token=${resp.data.access_token}; path=/; max-age=86400`
            }

            return resp.data
        } catch(err: any) {
            throw new Error(err.response?.data?.detail || 'Auth failed')
        }
    }

    async Register() {
        try {
            const resp = await axios.post('http://127.0.0.1:8001/api/create_user', {
                username: this.username,
                password: this.password
            })
            return resp.data
        } catch(err: any) {
            throw new Error(err.response?.data?.detail || 'Registration failed')
        }
    }
}