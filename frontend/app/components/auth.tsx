export default function AuthComponents() {
    return (
        <div>
            <h1>Войти в аккаунт</h1>
            <input 
                placeholder="username"
            />
            <input 
                placeholder="password"
                type="password"
            />
            <button>Войти</button>
            <div>Нет аккаунта</div>
        </div>
    )
}