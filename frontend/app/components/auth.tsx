'use client'
import { useState } from "react"
import Auth from "../script/auth"

export default function AuthComponents() {
    const [reg, setReg] = useState<boolean>(false)
    const [username, setUsername] = useState<string>('')
    const [password, setPassword] = useState<string>('')
    const [err, seterr] = useState<string>('')

    function toggleAuthMode() {
        setReg(prev => !prev)
        seterr('')
    }

    // const AuthScripts = new Auth

    async function handleAuth() {
        try {
            const auth = new Auth(username, password)
            let result
            if(reg) {
                result = await auth.Register()
                seterr('регистрация прошла успешно')
            } else {
                result = await auth.Auth()
                seterr('капут')
            }
            return result
        } catch(err) {
            throw err
        }
    }
    
    return (
        <>
            {reg ? (
            <div>
                <h1>Регистрация</h1>
                <input 
                    placeholder="username"
                    value={username}
                    onChange={(e)=>setUsername(e.target.value)}
                />
                <input 
                    placeholder="password"
                    type="password"
                    value={password}
                    onChange={(e)=>setPassword(e.target.value)}
                />
                <button>Зарегистрироваться</button>
                <div onClick={toggleAuthMode}>У меня есть аккаунт</div>
                <p>{err}</p>
            </div>
        ):(
            <div>
                <h1>Войти в аккаунт</h1>
                <input 
                    placeholder="username"
                    value={username}
                    onChange={(e)=>setUsername(e.target.value)}
                    
                />
                <input
                    placeholder="password"
                    type="password"
                    value={password}
                    onChange={(e)=>setPassword(e.target.value)}
                />
                <button onClick={handleAuth}>Войти</button>
                <div onClick={toggleAuthMode}>Нет аккаунта</div>
            </div>
        )}
        </>
    )
}