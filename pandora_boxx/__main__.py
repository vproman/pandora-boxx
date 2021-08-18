from aiohttp import web
import aiopg
import logging
from psycopg2 import errors

UniqueViolation = errors.lookup('23505')  # Correct way to Import the psycopg2 errors


async def database(app):
    """
    A function that, when the server is started, connects to postgresql,
    and after stopping it breaks the connection (after yield)
    """
    dsn = app['dsn']
    async with aiopg.create_pool(dsn) as pool:
        app['pool'] = pool
        yield
    logging.info('pool released')


routes = web.RouteTableDef()


@routes.get('/')
async def hello(request):
    return web.Response(status=200, text="OK")


@routes.get('/users/{id:\d+}')
async def get_user(request):
    pool = request.app['pool']
    id = request.match_info['id']
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("""
            SELECT id, username, email 
            FROM users
            WHERE id = %(id)s
            """, {'id': id})
            result = await cur.fetchone()
            if result is None:
                return web.Response(status=404, text="")
            id, username, email = result
            return web.json_response({'id': id, 'username': username, 'email': email}, status=200)


@routes.post('/users')
async def post_user(request):
    pool = request.app['pool']
    data = await request.json()
    username = data['username']
    email = data['email']
    try:
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("""
                INSERT INTO users (username, email)
                VALUES (%(username)s, %(email)s)
                RETURNING id, username, email
                """, {'username': username, 'email': email})
                id, username, email = await cur.fetchone()
                return web.json_response({'id': id, 'username': username, 'email': email}, status=201)
    except UniqueViolation:
        return web.json_response({"error": "username already in use", "data": data}, status=400)


def main(argv):
    app = web.Application()
    app['dsn'] = 'dbname=pandora_boxx host=127.0.0.1 sslmode=disable'
    app.add_routes(routes)
    app.cleanup_ctx.extend([
        database,
    ])
    return app
