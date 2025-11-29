import { NextResponse } from "next/server";
import { NextRequest } from "next/server";

const publicRoutes = ['/auth']

export function middleware(req: NextRequest) {
    const {pathname} = req.nextUrl

    const token = req.cookies.get('token')?.value
    const isAunteficated = !!token

    if(publicRoutes.some(route=>pathname===route)&&isAunteficated) {
        return NextResponse.redirect(new URL('/', req.url))
    }

    if(!isAunteficated &&
        !publicRoutes.some(route => pathname === route) &&
        !pathname.startsWith('/_next') &&
        !pathname.startsWith('/static')
    ) {
        return NextResponse.redirect(new URL('/auth', req.url))
    }

    return NextResponse.next()
}

export const config = {
    matcher: [
        '/((?!_next/static|_next/image|favicon.ico).*)',
    ],
}