import dropbox

# 1. Dropbox App Console에서 발급받은 App Key와 App Secret을 입력하세요.
APP_KEY = "1ii2zxyvjattedf"
APP_SECRET = "8co8pfh4n6ibpun"

# OAuth2 인증 흐름을 시작합니다.
# token_access_type='offline' 이 리프레시 토큰을 요청하는 핵심 파라미터입니다.
auth_flow = dropbox.DropboxOAuth2FlowNoRedirect(
    APP_KEY, 
    APP_SECRET, 
    token_access_type='offline'
)

# 사용자에게 인증을 요청할 URL을 생성합니다.
authorize_url = auth_flow.start()

print("1. 아래 URL을 웹 브라우저에서 열어주세요:")
print(authorize_url)
print("\n2. Dropbox 계정에 로그인하고 '허용(Allow)' 버튼을 클릭하세요.")
print("3. 생성된 인증 코드를 복사하여 아래에 붙여넣고 Enter 키를 누르세요.")

# 사용자로부터 인증 코드를 입력받습니다.
auth_code = input("인증 코드 입력: ").strip()

try:
    # 입력받은 인증 코드를 사용하여 액세스 토큰과 리프레시 토큰을 발급받습니다.
    oauth_result = auth_flow.finish(auth_code)
    
    # oauth_result.access_token  # 이것이 새로 발급된 단기 액세스 토큰입니다.
    # oauth_result.refresh_token # 이것이 우리가 필요한 영구적인 리프레시 토큰입니다.

    print("\n✅ 성공! 아래의 리프레시 토큰을 안전한 곳에 저장하세요.")
    print("="*50)
    print(f"REFRESH_TOKEN: {oauth_result.refresh_token}")
    print("="*50)
    print("\n이 토큰을 이제 메인 게임 코드에서 사용하게 됩니다.")

except Exception as e:
    print(f"\n❌ 오류 발생: {e}")