'use client'
import { useState } from "react"
import Auth from "../script/auth"
import { useRouter } from "next/navigation"

export default function AuthComponents() {
    const [reg, setReg] = useState<boolean>(false)
    const [username, setUsername] = useState<string>('')
    const [password, setPassword] = useState<string>('')
    const [err, setErr] = useState<string>('')
    const [loading, setLoading] = useState<boolean>(false)
    const router = useRouter()

    function toggleAuthMode() {
        setReg(prev => !prev)
        setErr('')
        setUsername('')
        setPassword('')
    }

    async function handleAuth() {
        if (!username || !password) {
            setErr('Заполните все поля')
            return
        }

        setLoading(true)
        setErr('')
        
        try {
            const auth = new Auth(username, password)
            let result
            
            if (reg) {
                result = await auth.Register()
                setErr('✅ Регистрация прошла успешно! Теперь войдите в аккаунт')
                setReg(false)
            } else {
                result = await auth.Auth()
                setErr('✅ Вход выполнен успешно!')
                console.log('Token:', result.access_token)
                
                if (result.access_token) {
                    localStorage.setItem('token', result.access_token)
                }
                router.push('/')
            }
        } catch (error: any) {
            setErr(`❌ ${error.message}`)
        } finally {
            setLoading(false)
        }
    }
    
    return (
        <div>
            {err && (
                <div>
                    {err}
                </div>
            )}
            
            {reg ? (
                <div>
                    <h1>Регистрация</h1>
                    <input 
                        placeholder="username"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        disabled={loading}
                    />
                    <input 
                        placeholder="password"
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        disabled={loading}
                    />
                    <button 
                        onClick={handleAuth}
                        disabled={loading}
                    >
                        {loading ? 'Загрузка...' : 'Зарегистрироваться'}
                    </button>
                    <div onClick={toggleAuthMode}>
                        У меня есть аккаунт
                    </div>
                </div>
            ) : (
                <div>
                    <h1>Войти в аккаунт</h1>
                    <input 
                        placeholder="username"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        disabled={loading}
                    />
                    <input
                        placeholder="password"
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        disabled={loading}
                    />
                    <button 
                        onClick={handleAuth}
                        disabled={loading}
                    >
                        {loading ? 'Загрузка...' : 'Войти'}
                    </button>
                    <div onClick={toggleAuthMode}>
                        Нет аккаунта
                    </div>
                </div>
            )}
        </div>
    )
}