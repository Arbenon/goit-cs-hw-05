import os
import asyncio
import aiofiles
import aiofiles.os
import logging
from pathlib import Path
import argparse

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Func for paths using ArgumentParser
def get_paths():
    parser = argparse.ArgumentParser(description="Копіювання файлів із сортуванням за розширенням.")
    parser.add_argument("source", help="Шлях до вихідної папки")
    parser.add_argument("destination", help="Шлях до цільової папки")
    args = parser.parse_args()
    return args.source, args.destination

# Async func for copying files
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

# Async func for reading folders recursively
async def read_folder(source_dir, dest_dir):
    tasks = []
    for entry in os.scandir(source_dir):
        if entry.is_file():
            file_path = Path(entry.path)
            tasks.append(copy_file(file_path, dest_dir))
        elif entry.is_dir():
            await read_folder(entry.path, dest_dir)  # рекурсивний виклик для обробки підпапок

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
