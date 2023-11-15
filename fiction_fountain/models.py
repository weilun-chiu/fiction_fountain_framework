from django.db import models
import openai
from contextlib import contextmanager
import threading
import time
import json

openai.api_key = "your open ai key"
assert openai.api_key != "your open ai key", "Specify your openai key before moving on"

class TimeoutException(Exception):
    def __init__(self, msg=''):
        self.msg = msg

@contextmanager
def time_limit(seconds, msg=''):
    
    timer = threading.Timer(seconds, lambda: _thread.interrupt_main())
    timer.start()
    try:
        yield
    except KeyboardInterrupt:
        raise TimeoutException("Timed out for operation {}".format(msg))
    finally:
        # if the action ends in specified time, timer is canceled
        timer.cancel()

def query_openai(prompt,
                 output_tokens_number = 1024,
                 retry=2):
    # return None for now
    print(f'query_openai with prompt: {prompt}')
    # return None
    for i in range(retry):
        try:
            response = openai.Completion.create(
                model="gpt-3.5-turbo-instruct",
                max_tokens=output_tokens_number, 
                prompt=prompt, 
                n=1, # num of returned sequence
            )
            print(response["choices"][0]["text"])
            return response["choices"][0]["text"]
        except:
            time.sleep(2)
    print(f'query_openai fail')
    return None

class FictionFountain(models.Model):
    genre = models.CharField(max_length=20)
    people = models.CharField(max_length=20)
    settings = models.TextField(default='')  # Store generated settings
    outlines = models.TextField(default='')  # Store generated outlines
    chapters = models.TextField(default='[]')  # Store chapters as a JSON-encoded list
    reading_progress = models.IntegerField(default=0)
    next_chapter_id = models.IntegerField(default=1)

    def __str__(self) -> str:
        genre = self.genre
        people = self.people
        return f'genre: {genre} people: {people}'

    def generate_settings(self) -> str:
        # Use OpenAI GPT-3.5 API to generate settings based on genre and people
        genre = self.genre
        people = self.people
        role = f'You are a {genre} author. Your task is to write {genre} stories for {people} in a vivid and intriguing language.'
        action = f'Fill out the template below for a {genre} story for {people}.'
        template = f'''
Title: [Insert story title here]

Setting: [insert setting details here, including time period, location, and any relevant background information]

Protagonist: [Insert protagonist's name, age, and occupation, as well as a brief description of their personality and motivations]

Antagonist: [Insert antagonist's name, age, and occupation, as well as a brief description of their personality and motivations]

Conflict: [Insert the main conflict of the story, including the problem the protagonist faces and the stakes involved]

Dialog: [Instructions for using dialogue to advance the plot, reveal character, and provide information to the reader]

Theme: [Insert the central theme of the story and instructions for developing it throughout the plot, character, and setting]

Tone: [Insert the desired tone for the story and instructions for maintaining consistency and appropriateness to the setting and characters]

Pacing: [Instructions for varying the pace of the story to build and release tension, advance the plot, and create dramatic effect]

Optional: Keep the each chapter around 300 words and at most 3 events, [insert and additional details or requirements for the story, such as genre constraints]
'''
        prompt = role + action + template
        generated_settings = query_openai(prompt=prompt)
        if generated_settings is None:
            return None
        self.settings = generated_settings
        self.save()

        return generated_settings

    def generate_chapter(self) -> str:
        chapter = None
        while self.reading_progress + 1 >= self.next_chapter_id:

            genre = self.genre
            people = self.people
            settings = self.settings
            if not settings:
                settings = self.generate_settings()
            next_chapter_id = self.next_chapter_id

            role = f'You are a {genre} author. Your task is to write {genre} stories for {people} in a vivid and intriguing language.'
            prompt = role + f'''
#### Setting ####

{settings}'''

            prompt_variation = ""
            previous_outline = self.outlines
            if previous_outline != "":
                prompt += f'''
#### Previous Chapters ####

{previous_outline}
'''
                prompt_variation = " and Previous Chapters"
            prompt += f'''
#### Instruction ####

Given the Setting{prompt_variation}, build the chapter {next_chapter_id} outline with following format, describe each event within 30 words:

#### Format ####

Chapter {next_chapter_id}
event [event_id]: [short description]
'''
            chapter_outline = query_openai(prompt=prompt)
            if chapter_outline is None:
                return None
            previous_outline += "\n" + chapter_outline
            self.outlines = previous_outline

            prompt = f'''
{role}
#### setting ####
{settings}
#### chapter outlines ####
{previous_outline} 
#### Instruction ####
Write chapter {self.next_chapter_id} in depth and in great detail, in an intriguing writing style:
Chapter {self.next_chapter_id} - [Chapter Title]
[Chapter Content]
'''
            chapter = query_openai(prompt=prompt)
            if chapter is None:
                return None
            chapter = chapter.splitlines()
            chapter = [p.strip() for p in chapter if p.strip()]

            # Append to self.chapters
            chapters_list = json.loads(self.chapters)
            chapters_list.append(chapter)
            self.chapters = json.dumps(chapters_list)
            next_chapter_id += 1
            self.next_chapter_id = next_chapter_id
            self.save()
        return chapter