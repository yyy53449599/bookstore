@echo off
setlocal

:: 设置当前目录为 PYTHONPATH
set PYTHONPATH=%cd%

:: 运行 coverage，并指定路径和参数
coverage run --timid --branch --source=fe,be --concurrency=thread -m pytest -v --ignore=fe\data

:: 合并覆盖率数据
coverage combine

:: 生成覆盖率报告
coverage report

:: 生成 HTML 覆盖率报告
coverage html

endlocal
