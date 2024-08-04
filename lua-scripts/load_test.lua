local json = require("cjson")

-- Configuration
local base_url = "http://localhost:30080"

-- Helper function to make HTTP requests
local function make_request(method, path, body)
    local headers = {}
    headers["Content-Type"] = "application/json"
    
    if wrk and wrk.headers and wrk.headers["Authorization"] then
        headers["Authorization"] = wrk.headers["Authorization"]
    end

    local url = base_url .. path
    
    if wrk and wrk.format then
        return wrk.format(method, url, headers, body)
    else
        -- If not running in wrk, return a table with request details
        return {
            method = method,
            url = url,
            headers = headers,
            body = body
        }
    end
end

-- User login function
local function req_user_login(username, password, verification_code)
    local body = json.encode({
        username = username,
        password = password,
        verificationCode = verification_code
    })
    
    return make_request("POST", "/api/v1/users/login", body)
end

-- User create function
local function req_user_create(username, password, user_id)
    local body = json.encode({
        userName = username,
        password = password,
        userId = user_id
    })
    
    return make_request("POST", "/api/v1/auth", body)
end

-- User delete function
local function req_user_delete(user_id)
    return make_request("DELETE", "/api/v1/users/" .. user_id, nil)
end

-- Request generator function
local function request()
    -- You can customize this part to generate different types of requests
    local r = math.random(1, 3)
    
    if r == 1 then
        return req_user_login("testuser", "password123", "1234")
    elseif r == 2 then
        return req_user_create("newuser", "newpassword", "user123")
    else
        return req_user_delete("user123")
    end
end

-- Response handler
local function response(status, headers, body)
    if status == 200 then
        local resp = json.decode(body)
        if resp.data and resp.data.token then
            if wrk and wrk.headers then
                wrk.headers["Authorization"] = "Bearer " .. resp.data.token
            end
        end
    end
end

-- Export functions
local M = {}
M.req_user_login = req_user_login
M.req_user_create = req_user_create
M.req_user_delete = req_user_delete
M.request = request
M.response = response

-- For wrk
if wrk then
    request = M.request
    response = M.response
end

return M