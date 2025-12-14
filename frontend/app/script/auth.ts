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
                const token = resp.data.access_token
                
                console.log('🔐 Получен токен:', token.substring(0, 20) + '...')
                
                // 1. Устанавливаем cookie для Next.js middleware
                document.cookie = `auth-token=${token}; path=/; max-age=${60 * 60 * 24 * 7}; SameSite=Strict`
                
                // 2. Дополнительно устанавливаем через серверный endpoint
                try {
                    await fetch('/api/set-auth-cookie', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ token }),
                    })
                    console.log('✅ Cookie установлена через API')
                } catch (e) {
                    console.warn('⚠️ Не удалось установить cookie через API:', e)
                }
                
                // 3. Сохраняем в localStorage для клиентского использования
                if (typeof window !== 'undefined') {
                    localStorage.setItem('token', token)
                    console.log('✅ Токен сохранен в localStorage')
                }
                
                // 4. Проверяем что cookie установилась
                setTimeout(() => {
                    const cookieToken = document.cookie
                        .split('; ')
                        .find(row => row.startsWith('auth-token='))
                        ?.split('=')[1]
                    
                    console.log('🔍 Проверка cookie после установки:', cookieToken ? 'успешно' : 'не найдена')
                }, 100)
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