'use client'
import { useState, useEffect } from "react"
import Auth from "../script/auth"
import { useRouter, useSearchParams } from "next/navigation"

export default function AuthComponents() {
    const [reg, setReg] = useState<boolean>(false)
    const [username, setUsername] = useState<string>('')
    const [password, setPassword] = useState<string>('')
    const [err, setErr] = useState<string>('')
    const [loading, setLoading] = useState<boolean>(false)
    const router = useRouter()
    const searchParams = useSearchParams()

    // Проверяем при загрузке, не авторизован ли пользователь
    useEffect(() => {
        const checkIfAlreadyAuthenticated = async () => {
            // Проверяем cookie
            const cookieToken = getCookie('auth-token')
            
            // Проверяем localStorage
            let localStorageToken = null
            if (typeof window !== 'undefined') {
                localStorageToken = localStorage.getItem('token')
            }
            
            const token = cookieToken || localStorageToken
            
            if (token) {
                try {
                    const response = await fetch('http://127.0.0.1:8001/api/check_auth', {
                        headers: {
                            'Authorization': `Bearer ${token}`,
                        },
                    })
                    
                    if (response.ok) {
                        const returnUrl = searchParams.get('from') || '/'
                        window.location.href = returnUrl
                    } else {
                        // Если токен невалидный, очищаем
                        clearAuthData()
                    }
                } catch (error) {
                    console.error('Ошибка проверки токена:', error)
                    clearAuthData()
                }
            }
        }
        
        checkIfAlreadyAuthenticated()
    }, [searchParams])

    // Функция для получения cookie
    const getCookie = (name: string): string | null => {
        if (typeof document === 'undefined') return null
        
        const value = `; ${document.cookie}`
        const parts = value.split(`; ${name}=`)
        
        if (parts.length === 2) {
            return parts.pop()?.split(';').shift() || null
        }
        return null
    }

    // Функция для очистки данных авторизации
    const clearAuthData = () => {
        // Очищаем cookie
        document.cookie = 'auth-token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT'
        
        // Очищаем localStorage
        if (typeof window !== 'undefined') {
            localStorage.removeItem('token')
        }
    }

    function toggleAuthMode() {
        setReg(prev => !prev)
        setErr('')
        setUsername('')
        setPassword('')
    }

    async function handleAuth() {
        if (!username.trim() || !password.trim()) {
            setErr('Заполните все поля')
            return
        }

        if (password.length < 3) {
            setErr('Пароль должен содержать минимум 3 символа')
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
                setUsername('')
                setPassword('')
            } else {
                result = await auth.Auth()
                setErr('✅ Вход выполнен успешно!')
                
                // Ждем немного для установки cookie
                await new Promise(resolve => setTimeout(resolve, 200))
                
                // Редирект на сохраненный URL или на главную
                const returnUrl = searchParams.get('from') || '/'
                window.location.href = returnUrl
            }
        } catch (error: any) {
            setErr(`❌ ${error.message}`)
        } finally {
            setLoading(false)
        }
    }

    // Обработка нажатия Enter
    const handleKeyPress = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter') {
            handleAuth()
        }
    }
    
    return (
        <div style={styles.container}>
            <div style={styles.authBox}>
                <h1 style={styles.title}>
                    {reg ? 'Регистрация' : 'Вход в аккаунт'}
                </h1>
                
                {err && (
                    <div style={{
                        ...styles.message,
                        backgroundColor: err.includes('✅') ? '#d4edda' : '#f8d7da',
                        color: err.includes('✅') ? '#155724' : '#721c24',
                        borderColor: err.includes('✅') ? '#c3e6cb' : '#f5c6cb'
                    }}>
                        {err}
                    </div>
                )}
                
                <div style={styles.form}>
                    <input 
                        placeholder="Имя пользователя"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        onKeyPress={handleKeyPress}
                        disabled={loading}
                        style={styles.input}
                    />
                    <input 
                        placeholder="Пароль"
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        onKeyPress={handleKeyPress}
                        disabled={loading}
                        style={styles.input}
                    />
                    
                    <button 
                        onClick={handleAuth}
                        disabled={loading}
                        style={{
                            ...styles.button,
                            opacity: loading ? 0.7 : 1,
                            cursor: loading ? 'not-allowed' : 'pointer'
                        }}
                    >
                        {loading ? (
                            <span style={styles.loading}>
                                <span style={styles.spinner}></span>
                                Загрузка...
                            </span>
                        ) : reg ? 'Зарегистрироваться' : 'Войти'}
                    </button>
                    
                    <div 
                        onClick={toggleAuthMode}
                        style={styles.toggle}
                    >
                        {reg ? 'Уже есть аккаунт? Войти' : 'Нет аккаунта? Зарегистрироваться'}
                    </div>
                </div>
            </div>
        </div>
    )
}

const styles = {
    container: {
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '100vh',
        backgroundColor: '#f5f5f5',
        padding: '20px'
    },
    authBox: {
        backgroundColor: 'white',
        borderRadius: '10px',
        boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
        padding: '40px',
        width: '100%',
        maxWidth: '400px'
    },
    title: {
        textAlign: 'center' as const,
        marginBottom: '30px',
        color: '#333',
        fontSize: '24px'
    },
    message: {
        padding: '12px',
        borderRadius: '6px',
        marginBottom: '20px',
        border: '1px solid',
        fontSize: '14px'
    },
    form: {
        display: 'flex',
        flexDirection: 'column' as const,
        gap: '15px'
    },
    input: {
        padding: '12px 15px',
        border: '1px solid #ddd',
        borderRadius: '6px',
        fontSize: '16px',
        outline: 'none',
        transition: 'border-color 0.3s',
        ':focus': {
            borderColor: '#007bff'
        }
    },
    button: {
        padding: '12px',
        backgroundColor: '#007bff',
        color: 'white',
        border: 'none',
        borderRadius: '6px',
        fontSize: '16px',
        fontWeight: 'bold' as const,
        cursor: 'pointer',
        transition: 'background-color 0.3s',
        ':hover': {
            backgroundColor: '#0056b3'
        }
    },
    loading: {
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: '8px'
    },
    spinner: {
        display: 'inline-block',
        width: '16px',
        height: '16px',
        border: '2px solid rgba(255,255,255,.3)',
        borderRadius: '50%',
        borderTopColor: '#fff',
        animation: 'spin 1s ease-in-out infinite',
        '@keyframes spin': {
            'to': { transform: 'rotate(360deg)' }
        }
    },
    toggle: {
        textAlign: 'center' as const,
        color: '#007bff',
        cursor: 'pointer',
        fontSize: '14px',
        marginTop: '10px',
        ':hover': {
            textDecoration: 'underline'
        }
    }
}