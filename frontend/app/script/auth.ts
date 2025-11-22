import axios from 'axios'

export default class Auth {
    private username: string
    private password: string
    
    constructor(username:string, password:string){
        this.username = username
        this.password = password
    }

    async Auth() {
        try {
            const resp = await axios.post('http://localhost:8000/api/auth', {
                headers: {
                    'username': this.username,
                    'password': this.password
                }
            })
            return resp.data
        } catch(err) {
            throw err
        }
    }

    async Register() {
        try {
            const resp = await axios.post('http://localhost:8000/api/create_user', {
                headers: {
                    'username': this.username,
                    'password': this.password
                }
            })
            return resp.data
        } catch(err) {
            throw err
        }
    }
}