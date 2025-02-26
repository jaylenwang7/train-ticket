
type SvcImpl struct {
	cli     *httpclient.HttpClient
	BaseUrl string
}

func NewSvcClients() *SvcImpl {
	cli := httpclient.NewCustomClient()
	cli.AddHeader("Proxy-Connection", "keep-alive")

	cli.AddHeader("Accept", "application/json")
	cli.AddHeader("X-Requested-With", "XMLHttpRequest")
	cli.AddHeader("User-Agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36")
	cli.AddHeader("Content-Type", "application/json")
	cli.AddHeader("Accept-Language", "zh-CN,zh;q=0.9,en;q=0.8")
	cli.AddHeader("Connection", "keep-alive")
	baseUrl := os.Getenv("BASE_URL")
	if baseUrl == "" {
		panic("PLEASE use BASE_URL environment variable, example: BASE_URL=http://127.0.0.1:8080")
	}
	return &SvcImpl{
		cli:     cli,
		BaseUrl: baseUrl,
	}
}

func GetBasicClient() (*SvcImpl, string) {
	cli := NewSvcClients()
	loginResp, _ := cli.ReqUserLogin(&UserLoginInfoReq{
		Password:         "111111",
		UserName:         "fdse_microservice",
		VerificationCode: "123",
	})
	return cli, loginResp.Data.UserId
}
func GetAdminClient() (*SvcImpl, string) {
	cli := NewSvcClients()
	loginResp, err := cli.ReqUserLogin(&UserLoginInfoReq{
		Password:         "222222",
		UserName:         "admin",
		VerificationCode: "123",
	})
	fmt.Println(loginResp, err)
	return cli, loginResp.Data.UserId
}

func TestSvcImpl_ReqUserCreate(t *testing.T) {
	// create
	cli := NewSvcClients()
	RegisterResp, err := cli.ReqUserCreate(&UserCreateInfoReq{
		Password: "testpasswd",
		UserName: "testuser",
		UserId:   uuid.New().String(),
	})
	if err != nil {
		t.Errorf("Request failed, err %s", err)
	}
	if RegisterResp.Status != 1 {
		t.Errorf("RegisterResp.Status != 1")
	}

	// login
	loginResp, err := cli.ReqUserLogin(&UserLoginInfoReq{
		Password:         "222222",
		UserName:         "admin",
		VerificationCode: "123",
	})
	if err != nil {
		t.Error(err)
	}
	if loginResp.Status != 1 {
		t.Errorf("RegisterResp.Status != 1")
	}
	if loginResp.Data.Username != "admin" {
		t.Errorf("RegisterResp.Data.Username != \"admin\"")
	}

	// delete
	deleteResp, err := cli.ReqUserDelete(RegisterResp.Data.UserId)
	if err != nil {
		t.Errorf("Request failed, err %s", err)
	}
	if deleteResp.Status != 1 {
		t.Errorf("deleteResp.Status != 1")
	}
}