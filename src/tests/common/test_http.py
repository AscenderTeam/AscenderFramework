from pytest import mark

from ascender.common.http import HTTPClient, FormData, FileData
from ascender.core import inject


@mark.asyncio
async def test_file_upload():
    http = inject(HTTPClient)
    
    resp = await http.post(
        url="http://httpbin.org/post",
        content=FormData(
        file=FileData(
                filename="test.txt", 
                content=b"Hello, World!", 
                content_type="text/plain"
            )
        )
    )
    
    assert resp is not None