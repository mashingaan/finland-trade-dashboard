#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для чтения документа с заданием
"""

from docx import Document

def read_task_document():
    """Читаем документ с заданием"""
    
    doc = Document('/workspace/user_input_files/Задание_Внешняя_торговля.docx')
    
    full_text = []
    for paragraph in doc.paragraphs:
        if paragraph.text.strip():
            full_text.append(paragraph.text)
    
    # Сохраняем в файл
    with open('/workspace/docs/task_description.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(full_text))
    
    print("Содержимое документа:")
    print('\n'.join(full_text))

if __name__ == "__main__":
    read_task_document()
