import dropbox
import os

def upload_to_dropbox(access_token, file_path, dropbox_folder_path):
    """
    Dropbox에 파일을 업로드하고 공유 가능한 링크를 반환합니다.

    Args:
        access_token (str): Dropbox API Access Token.
        file_path (str): 업로드할 로컬 파일의 경로.
        dropbox_folder_path (str): Dropbox 내에 파일을 저장할 경로 (예: '/uploads/').

    Returns:
        str: 공유 가능한 URL.
    """
    # Dropbox 객체 생성
    try:
        dbx = dropbox.Dropbox(access_token)
        dbx.users_get_current_account() # 토큰 유효성 검사
        print("Dropbox 계정 연결 성공.")
    except dropbox.exceptions.AuthError:
        print("오류: Access Token이 유효하지 않습니다. 다시 확인해주세요.")
        return None

    # 파일 업로드
    try:
        with open(file_path, 'rb') as f:
            # Dropbox에 저장할 파일 경로 설정
            file_name = os.path.basename(file_path)
            dropbox_path = os.path.join(dropbox_folder_path, file_name).replace('\\', '/')
            
            print(f"'{file_path}' 파일을 Dropbox의 '{dropbox_path}' 경로에 업로드 중...")
            
            # files_upload: 파일을 업로드하는 API
            # mode=dropbox.files.WriteMode('overwrite')는 덮어쓰기 옵션
            dbx.files_upload(f.read(), dropbox_path, mode=dropbox.files.WriteMode('overwrite'))
            print("업로드 완료!")

        # 업로드된 파일의 공유 링크 생성
        share_link_metadata = dbx.sharing_create_shared_link_with_settings(dropbox_path)
        share_link = share_link_metadata.url
        print(f"공유 링크 생성: {share_link}")
        
        # Dropbox 공유 링크는 직접 다운로드 링크가 아님
        # 끝에 ?dl=0을 ?dl=1로 바꿔주면 바로 다운로드가능한 링크가 됨
        download_link = share_link.replace('?dl=0', '?dl=1')
        print(f"직접 다운로드 링크: {download_link}")
        
        return download_link
        
    except Exception as e:
        print(f"파일 업로드 또는 링크 생성 중 오류 발생: {e}")
        return None

# --- 테스트 코드 실행 ---
if __name__ == "__main__":
    # 이 부분은 본인의 정보로 바꿔야 합니다.
    # 1. Dropbox 개발자 웹사이트에서 발급받은 Access Token
    DROPBOX_ACCESS_TOKEN = "sl.u.AF-MUh8FpDgqnVBb2UqSwFZJbmGBJT80FT2x9dVM3A3YePU2zZlRLv6mumFiwysV2_WasQG7F6XWwonrvV1ysMZ4iBce3X2FeBBTPyoJcf6tF_q7p8KfR-1Q9ilDBX1aG-EFe47mA0nMicd-X17rdjkyd8Q59jZqVISkg6Otvba6UR0X6NBdPjFVoJwHVRJdgWnKImW74HJQ2T555LcM-DDFG-VzEExopTsJTfoXTinrIbIsvkUgQ7wmEskABnxkr3P1qxWahqjF4SaYhI91xmle_ln6Sx8EFJI-2yd5pYW3cm7-Uuu9joVtlsSspw_MfgtkbVbZ6NF1Y4IrDSs_VYWk4B2W9xN9uh7hTAjmr-EG3AL3p_VWKpKv42W9NP9LEwzxzH98x8hINX9TfKqbmgMokeXzW2RmYe49yoZSOqIJ48sfVF3lpyFSEdk_VIgs4QFdX4rk_LMC0eLfwdj4zJanyzGCM5LagWaGiW0zTIrFg6qbUmbjsLFNKl5PjVU7TTf7IYhnihPJqUMaDIqpFUOgc6wUnGyzxQufFdpfStUD81PUN-YE7LQ68bRejnB9un1zpzmVXG4yVoppvtEhlFVkfP2LHjV0XDgFM9LKgzW1A7HoGriAgFBnrG4tz6tzjFPcJeO14HhyWabwOlgp22i7o7PUzBpbIGKcrJPX9w98bj9QYZrdyma_bRfWtVonqo9PC0ePJz3a_t2ggnoBUhilZErcsuHBHr6eDUoeb9eTnKswWIzJYBgt869xI5mjcJXq6P4IhOPl0SmSzRRiPq_O0q9o3JZSxtI6MBgrcO5SFJvTbISCRZqdpUK3f4bXEzncbxHL-p0opfvzq0y2yE9Y4x4u54gP33aJzILtvlm838OHKL7kX01OsVrvdleEEhVGMO7IOrduL-jGDJv5LTIXclUo3fk8Cbb5IfcXyK-Dbg04RxUu1D5avMkppPEUCe8Pego6p785U3DEaAp8wasGKMqqFcONFzaz9TFdX6EvlFJvwnVwB6eiCQwIdJ-PZUto2fdTI7ASlqtECaposK4sC3Emvt7m-6pYq5Cr6LxpWPI-Hc-FO97u8fWY7PfEeH9RTr5nzYWZqtdHgQSTQ8eZaQCqfn9u-Kv2IcyNrvzZ--JTQHUM_WbUKd8i1Rpa-UJTIg74KBPHoKdp3VpG5THqBr6dqA72f8kCDxX_Abm59dGok5DQFBz7ULLWfwwVFLgQr2t-t-gg7p29RsIJlonWOoDyYQXZAhSDAUHwT3Lkpp_tRLRDRvdbARzfAaSpTWAvHIZzm-_fwWPRy9FuLv6EDxgtC3hBHEVf3_7cZKfsDW3FvJi98GZCWUNttGkt6c9Iq1kHlpgPiR2Du1SZtTHYKd4HwwEgrgWwPDYcZ54imjaCz8nJ6J0yMlK8LdaoQ89YVW5IvvNGuc2Nuk_nY53OquG_eyT6V4MfDCjXeTbqRg" 
    
    # 2. 업로드할 로컬 파일 경로
    LOCAL_FILE_PATH = "./results/combined_images/combined_4b80fe15_20250901_212622.png"
    
    # 3. Dropbox 내에 파일을 저장할 폴더 경로
    #   (폴더가 존재하지 않으면 자동으로 생성됨)
    DROPBOX_UPLOAD_FOLDER = "/uploads/csmonster_images"

    if DROPBOX_ACCESS_TOKEN == "YOUR_ACCESS_TOKEN_HERE":
        print("⚠️ Dropbox Access Token을 설정해주세요.")
    else:
        upload_link = upload_to_dropbox(
            DROPBOX_ACCESS_TOKEN, 
            LOCAL_FILE_PATH, 
            DROPBOX_UPLOAD_FOLDER
        )
        if upload_link:
            print(f"최종 업로드 완료: {upload_link}")