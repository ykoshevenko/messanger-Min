import { NextResponse } from 'next/server'

export async function POST(request: Request) {
    try {
        const { token } = await request.json()
        
        const response = NextResponse.json({ success: true })
        
        // Устанавливаем cookie на сервере
        response.cookies.set({
            name: 'auth-token',
            value: token,
            httpOnly: false, // Делаем доступной для JS
            secure: process.env.NODE_ENV === 'production',
            sameSite: 'lax',
            maxAge: 60 * 60 * 24 * 7, // 7 дней
            path: '/',
        })
        
        return response
    } catch (error) {
        return NextResponse.json(
            { error: 'Failed to set cookie' },
            { status: 500 }
        )
    }
}