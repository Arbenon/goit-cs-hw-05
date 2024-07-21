import os
import asyncio
import aiofiles
import aiofiles.os
import logging
from pathlib import Path

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Func for paths
def get_paths():
    source = input("Введіть шлях до вихідної папки: ")
    destination = input("Введіть шлях до цільової папки: ")
    return source, destination

# Async func for coping files
async def copy_file(file_path, dest_dir):
    ext = file_path.suffix.lstrip('.').lower()
    target_folder = dest_dir / ext

    if not await aiofiles.os.path.exists(target_folder):
        await aiofiles.os.makedirs(target_folder, exist_ok=True)

    dest_path = target_folder / file_path.name

    async with aiofiles.open(file_path, 'rb') as f_src:
        async with aiofiles.open(dest_path, 'wb') as f_dst:
            while True:
                chunk = await f_src.read(1024)
                if not chunk:
                    break
                await f_dst.write(chunk)

    logging.info(f"Файл {file_path} скопійовано до {dest_path}")

# Async func for reading files
async def read_folder(source_dir, dest_dir):
    tasks = []
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            file_path = Path(os.path.join(root, file))
            tasks.append(copy_file(file_path, Path(dest_dir)))

    if tasks:
        await asyncio.gather(*tasks)

# Main program
async def main():
    source, destination = get_paths()
    source_dir = Path(source)
    dest_dir = Path(destination)

    if not await aiofiles.os.path.exists(source_dir):
        print(f"Вихідна папка '{source_dir}' не існує.")
        return
    
    if not await aiofiles.os.path.exists(dest_dir):
        await aiofiles.os.makedirs(dest_dir, exist_ok=True)

    try:
        await read_folder(source_dir, dest_dir)
        print(f"Файли успішно скопійовані та відсортовані до '{dest_dir}'")
    except Exception as e:
        print(f"Виникла помилка: {e}")

if __name__ == "__main__":
    asyncio.run(main())
