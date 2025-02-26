local load_test = require("load_test")

-- Mock wrk environment if it doesn't exist
if not wrk then
    wrk = {
        headers = {}
    }
end

-- Helper function to print request details
local function print_request(req)
    print("Method: " .. req.method)
    print("URL: " .. req.url)
    print("Headers:")
    for k, v in pairs(req.headers) do
        print("  " .. k .. ": " .. v)
    end
    if req.body then
        print("Body: " .. req.body)
    end
end

-- Test user login
print("Testing user login:")
local login_req = load_test.req_user_login("testuser", "password123", "1234")
print_request(login_req)
print("\n")

-- Test user create
print("Testing user create:")
local create_req = load_test.req_user_create("newuser", "newpassword", "user123")
print_request(create_req)
print("\n")

-- Test user delete
print("Testing user delete:")
local delete_req = load_test.req_user_delete("user123")
print_request(delete_req)
print("\n")

-- Test request generation
print("Testing random request generation:")
for i = 1, 5 do
    print("Request " .. i .. ":")
    local req = load_test.request()
    print_request(req)
    print("\n")
end

-- Test response handling
print("Testing response handling:")
local mock_response_body = [[
{
    "status": 200,
    "msg": "Success",
    "data": {
        "userId": "user123",
        "username": "testuser",
        "token": "mock_token_12345"
    }
}
]]
load_test.response(200, {}, mock_response_body)
print("Authorization header after response:", wrk.headers["Authorization"])