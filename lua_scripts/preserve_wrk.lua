local cjson = require("cjson")
local math = require("math")

-- Helper functions
local function random_boolean()
    return math.random(0, 1) == 1
end

local function random_phone()
    return tostring(math.random(10000000000, 99999999999))
end

local function random_str()
    local length = math.random(5, 10)
    local res = ""
    for i = 1, length do
        res = res .. string.char(math.random(97, 122))
    end
    return res
end

local function random_form_list(list)
    return list[math.random(#list)]
end

-- Constants
local uuid = "4d2a46c7-71cb-4cf1-b5bb-b68406d9da6f"
local date = os.date("%Y-%m-%d")
local base_address = "http://localhost:30080"

-- Main function
function query_and_preserve()
    local headers = {
        ["Cookie"] = "JSESSIONID=823B2652E3F5B64A1C94C924A05D80AF; YsbCaptcha=2E037F4AB09D49FA9EE3BE4E737EAFD2",
        ["Authorization"] = "Bearer eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJmZHNlX21pY3Jvc2VydmljZSIsInJvbGVzIjpbIlJPTEVfVVNFUiJdLCJpZCI6IjRkMmE0NmM3LTcxY2ItNGNmMS1iNWJiLWI2ODQwNmQ5ZGE2ZiIsImlhdCI6MTYyNzE5OTA0NCwiZXhwIjoxNjI3MjAyNjQ0fQ.3IIwwz7AwqHtOFDeXfih25i6_7nQBPL_K7BFxuyFiKQ",
        ["Content-Type"] = "application/json"
    }

    local start, end_place, trip_ids, preserve_url
    local high_speed = random_boolean()

    if high_speed then
        start = "Shang Hai"
        end_place = "Su Zhou"
        trip_ids = {1, 2, 3} -- Simulated high-speed ticket query
        preserve_url = base_address .. "/api/v1/preserveservice/preserve"
    else
        start = "Shang Hai"
        end_place = "Nan Jing"
        trip_ids = {4, 5, 6} -- Simulated normal ticket query
        preserve_url = base_address .. "/api/v1/preserveotherservice/preserveOther"
    end

    local base_preserve_payload = {
        accountId = uuid,
        assurance = "0",
        contactsId = "",
        date = date,
        from = start,
        to = end_place,
        tripId = ""
    }

    base_preserve_payload.tripId = random_form_list(trip_ids)

    if random_boolean() then
        base_preserve_payload.foodType = "1"
    else
        base_preserve_payload.foodType = "0"
    end

    if random_boolean() then
        base_preserve_payload.assurance = "1"
    end

    base_preserve_payload.contactsId = tostring(math.random(1, 5))
    base_preserve_payload.seatType = tostring(math.random(2, 3))

    if random_boolean() then
        base_preserve_payload.consigneeName = random_str()
        base_preserve_payload.consigneePhone = random_phone()
        base_preserve_payload.consigneeWeight = math.random(1, 10)
        base_preserve_payload.handleDate = date
    end

    local payload = cjson.encode(base_preserve_payload)

    local request = wrk.format("POST", preserve_url, headers, payload)
    return request
end

-- Set up the request function for wrk
request = query_and_preserve