import asyncio
import pytest
from core.utils import async_retry

@pytest.mark.asyncio
async def test_async_retry_success():
    call_count = 0
    
    @async_retry(max_retries=3, initial_delay=0.01)
    async def success_func():
        nonlocal call_count
        call_count += 1
        if call_count < 2:
            raise ValueError("Fail first")
        return "success"

    result = await success_func()
    assert result == "success"
    assert call_count == 2

@pytest.mark.asyncio
async def test_async_retry_max_failures():
    @async_retry(max_retries=2, initial_delay=0.01)
    async def fail_func():
        raise ValueError("Always fail")

    with pytest.raises(ValueError, match="Always fail"):
        await fail_func()
