import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

// Публичные пути (доступны без авторизации)
const publicPaths = ['/auth', '/_next', '/favicon.ico']

export async function middleware(request: NextRequest) {
    const { pathname } = request.nextUrl
    
    console.log(`🔐 Middleware проверяет: ${pathname}`)
    
    // Проверяем, является ли путь публичным
    const isPublicPath = publicPaths.some(publicPath => 
        pathname === publicPath || pathname.startsWith(publicPath + '/')
    )
    
    // Если путь публичный - пропускаем
    if (isPublicPath) {
        console.log(`✅ Публичный путь: ${pathname}`)
        return NextResponse.next()
    }
    
    // Получаем токен из cookies
    const token = request.cookies.get('auth-token')?.value
    
    // Если токен есть - проверяем его
    if (token) {
        try {
            const response = await fetch('http://127.0.0.1:8000/api/check_auth', {
                headers: {
                    'Authorization': `Bearer ${token}`,
                },
            })
            
            if (response.ok) {
                console.log(`✅ Токен валиден для пути: ${pathname}`)
                
                // Если пользователь авторизован и пытается зайти на /auth - редирект на главную
                if (pathname === '/auth') {
                    console.log('🔄 Авторизованный пользователь пытается зайти на /auth, редирект на /')
                    return NextResponse.redirect(new URL('/', request.url))
                }
                
                // Пропускаем авторизованного пользователя
                return NextResponse.next()
            } else {
                console.log('❌ Токен невалиден')
                // Токен невалиден, удаляем его
                const redirectResponse = NextResponse.redirect(new URL('/auth', request.url))
                redirectResponse.cookies.delete('auth-token')
                return redirectResponse
            }
        } catch (error) {
            console.error('❌ Ошибка при проверке токена:', error)
            // Ошибка сети, редирект на auth
            const redirectResponse = NextResponse.redirect(new URL('/auth', request.url))
            redirectResponse.cookies.delete('auth-token')
            return redirectResponse
        }
    }
    
    // Если токена нет - редирект на /auth
    console.log(`🔒 Нет токена для пути: ${pathname}, редирект на /auth`)
    
    // Сохраняем текущий URL для возврата после логина
    const authUrl = new URL('/auth', request.url)
    authUrl.searchParams.set('from', pathname)
    
    return NextResponse.redirect(authUrl)
}

export const config = {
    matcher: [
        /*
         * Матчим все пути кроме:
         * - статических файлов (_next/static, _next/image, favicon.ico)
         * - файлов в public директории
         */
        '/((?!_next/static|_next/image|favicon.ico|public/).*)',
    ],
}