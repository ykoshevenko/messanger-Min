import '../style/auth.css'

export default function AuthComponent() {
    return (
        <div>
            <div className="flex-1 flex justify-center items-center">
                    <form  className="flex flex-col items-center w-200 h-180 p-25 bg-white rounded gap-4">
                        <h1 className="text-6xl">Регистрация</h1>
                        <input 
                            
                            
                            placeholder="Логин"
                            required
                            className="w-100 border-1 h-13 text-2xl"
                        />
                        <input
                            type="password"
                            
                            placeholder="Пароль"
                            required
                            className="w-100 border-1 h-13 text-2xl"
                        />
                        
                        <button className="rounded-lg button-color text-xl w-70 h-15 text-white" type="submit">Зарегистрироваться</button>
                        <button className='underline text-xl'  type="button" >
                            Уже есть аккаунт
                        </button>
                    </form>
                </div>
        </div>
    )
}