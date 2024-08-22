#!/usr/bin/env python3
import os
import sys
import time

class Record():
    def __init__(self, key:str, value:float):
        self.key:str=key
        self.value:float=value

class TimeIt():
    def __init__(self):
        self.start_time=time.time()
        self.journal:list[Record]=[]
        self.journal.append(Record(key="start_time", value=self.start_time))
    
    def print(self, text:str|None=None):
        if text is None:
            text="record"
        current_time=time.time()
        delta=current_time-self.start_time
        self.journal.append(Record(key=text, value=current_time))
        self._print(text, delta)

    def print_from(self, key:str|None=None):
        delta:float
        current_time=time.time()
        if key is None:
            record=self.journal[-1]
            delta=current_time-record.value
            self._print(record.key, delta, is_delta=True)
        else:
            for record in self.journal:
                if record.key == key:
                    delta=current_time-record.value
                    self._print(record.key, delta, is_delta=True)
        self.journal.append(Record(key="record", value=current_time))

    def _to_ms(self, value:float):
        return int(round(value, 3)*1000)
    
    def _print(self, key:str, value: float, is_delta=False):
        delta_text="[delta] at "
        delta=" "*len(delta_text)
        if is_delta is True:
            key=f"{key} (delta)"
        print(f">>> {self._to_ms(value):>10} ms: {key:<15}")
        
            
    


