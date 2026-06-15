# ShortenLink

| Vai trò | Domain | Chạy ở đâu |
|---------|--------|------------|
| Web UI | `adminphanmemvip.xyz` | Next.js **port 3000** |
| API | `api.adminphanmemvip.xyz` | FastAPI **port 8000** |
| Link ngắn (redirect) | `/{mã}` | Xem bên dưới |

## Vì sao `/qC7sTp` không có gì?

Tunnel Cloudflare trỏ `` → **port 9004**, nhưng **không có process nào** đang listen port đó → trình duyệt trống / lỗi kết nối.

**Không cần** chạy Next.js trên 9004. Backend đã có sẵn `GET /{code}` redirect.

## Cách 1 — Đơn giản nhất (khuyên dùng)

Trong Cloudflare Zero Trust, sửa Public Hostname:

| Hostname | Service |
|----------|---------|
| `` | `http://127.0.0.1:8000` |

Cùng backend với API, nhưng:
- `api.adminphanmemvip.xyz` → gọi `/api/links`
- `/qC7sTp` → gọi `/{code}` → redirect URL gốc

Chỉ cần backend đang chạy:

```powershell
cd backend
.\.venv\Scripts\activate
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Cách 2 — Port 9004 riêng (proxy nhẹ)

Nếu muốn tách process (tunnel vẫn trỏ 9004):

```powershell
# Terminal 1 — API + redirect logic
cd backend
.\.venv\Scripts\activate
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Terminal 2 — chỉ proxy /{code} → backend
cd redirect-service
.\start.ps1
```

Tunnel: `` → `http://127.0.0.1:9004`

## Web + API (như cũ)

```powershell
cd frontend
npm run dev
# .env.local: NEXT_PUBLIC_API_URL=https://api.adminphanmemvip.xyz
```

| Hostname | Service |
|----------|---------|
| `adminphanmemvip.xyz` | `http://localhost:3000` |
| `api.adminphanmemvip.xyz` | `http://localhost:8000` |

## Kiểm tra nhanh

```powershell
# Backend có link qC7sTp không?
curl http://127.0.0.1:8000/qC7sTp -I

# Hoặc qua redirect-service (nếu dùng cách 2)
curl http://127.0.0.1:9004/qC7sTp -I
```

Phải thấy `307` (hoặc `200` HTML nếu có mật khẩu/meta) và header `Location` trỏ URL đích.
