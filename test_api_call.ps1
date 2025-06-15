# PowerShell script để gọi API và tạo Project mới
$headers = @{
    "Content-Type" = "application/json"
}

$body = @{
    "title" = "Kiểm tra dữ liệu thực"
    "description" = "Dự án tạo để kiểm tra lưu dữ liệu vào Neo4j Aura"
} | ConvertTo-Json

Write-Host "Đang gửi yêu cầu POST đến API để tạo Project mới..."
try {
    $response = Invoke-WebRequest -Uri "http://127.0.0.1:8002/api/v1/projects/" -Method Post -Headers $headers -Body $body
    Write-Host "Kết quả trả về:"
    Write-Host "Status code: $($response.StatusCode)"
    Write-Host "Content: $($response.Content)"
} catch {
    Write-Host "Lỗi khi gọi API: $_"
}

# Tạm dừng
Write-Host "`nNhấn Enter để tiếp tục..."
