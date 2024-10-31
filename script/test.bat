@echo off
setlocal

echo 设置当前目录为 PYTHONPATH
set PYTHONPATH=%cd%

echo 运行 coverage，并指定路径和参数
coverage run --timid --branch --source=fe,be --concurrency=thread -m pytest -v --ignore=fe\data

echo 合并覆盖率数据
coverage combine

echo 生成覆盖率报告
coverage report

echo 生成 HTML 覆盖率报告
coverage html

endlocal
