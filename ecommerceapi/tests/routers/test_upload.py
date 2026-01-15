import contextlib
import pathlib
import tempfile

import pytest
from httpx import AsyncClient


@pytest.fixture()
def sample_image(fs) -> pathlib.Path:
    path = (pathlib.Path(__file__).parent / "assets" / "myfile.png").resolve()
    fs.create_file(path)
    return path


@pytest.fixture(autouse=True)
def mock_b2_upload_file(mocker):
    return mocker.patch(
        "ecommerceapi.routers.upload.b2_upload_file",
        return_value="https://fakeurl.com",
    )


@pytest.fixture(autouse=True)
def aiofiles_mock_open(mocker, fs):
    mocker_open = mocker.patch("aiofiles.open")

    @contextlib.asynccontextmanager
    async def async_file_open(fname: str, mode: str = "r"):
        out_fs_mock = mocker.AsyncMock(name=f"async_file_open:{fname!r}/{mode!r}")
        with open(fname, mode) as fin:
            out_fs_mock.read.side_effect = fin.read
            out_fs_mock.write.side_effect = fin.write
            yield out_fs_mock

    mocker_open.side_effect = async_file_open
    return mocker_open


async def call_upload_endpoint(async_client, token: str, file_path: pathlib.Path):
    return await async_client.post(
        "/upload",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": (file_path.name, file_path.read_bytes(), "image/png")},
    )


@pytest.mark.anyio
async def test_upload_image(
    async_client: AsyncClient, logged_with_token: str, sample_image: pathlib.Path
):
    response = await call_upload_endpoint(async_client, logged_with_token, sample_image)
    assert response.status_code == 201
    assert response.json()["file_url"] == "https://fakeurl.com"


@pytest.mark.anyio
async def test_temp_file_removed_after_upload(
    async_client: AsyncClient,
    logged_with_token: str,
    sample_image: pathlib.Path,
    mocker,
):
    named_temp_file_spy = mocker.spy(tempfile, "NamedTemporaryFile")
    response = await call_upload_endpoint(async_client, logged_with_token, sample_image)
    assert response.status_code == 201

    created_temp_file_path = named_temp_file_spy.return_value.name
    assert not pathlib.Path(created_temp_file_path).exists()
