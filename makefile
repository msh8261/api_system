
test_login:
	docker exec -it app curl -X POST "http://localhost:8022/login" -H "Content-Type: application/json" -d "{\"username\": \"test_user\", \"password\": \"test123\"}"

test_chat:
	docker exec -it app curl -i -X POST "http://localhost:8022/chat" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0X3VzZXIiLCJleHAiOjE3Mzg0NjM0MzV9._01AASibG7wKnHA0gvSu1RzuGmTfgs6tJM2Rj6_82P0" \
  -d '{"message": "Hello"}'

test_register:
  docker exec -it app curl -X POST "http://localhost:8022/register" -H "Content-Type: application/json" -d "{\"username\": \"user2\", \"password\": \"123\"}"
