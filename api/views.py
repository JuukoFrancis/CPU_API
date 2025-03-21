# import json
import heapq
from collections import deque
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from collections import deque
# Create your views here.


def fcfs(processes):
    time = 0
    result = []
    for process in processes:
        waiting_time = max(0, time)
        completion_time = time + process['burst_time']
        turnaround_time = completion_time
        result.append({'id': process['id'], 'completion_time': completion_time,
                      'waiting_time': waiting_time, 'turnaround_time': turnaround_time})
        time = completion_time
    return result


def sjf_preemptive(processes):
    processes.sort(key=lambda x: (x['arrival_time'], x['burst_time']))
    time = 0
    result = []
    remaining_time = {p['id']: p['burst_time'] for p in processes}
    completion_times = {}
    waiting_times = {}
    turnaround_times = {}
    completed = 0
    while completed < len(processes):
        available_processes = [
            p for p in processes if p['arrival_time'] <= time and remaining_time[p['id']] > 0]
        if available_processes:
            current = min(available_processes,
                          key=lambda x: remaining_time[x['id']])
            remaining_time[current['id']] -= 1
            if remaining_time[current['id']] == 0:
                completed += 1
                completion_times[current['id']] = time + 1
                turnaround_times[current['id']
                                 ] = completion_times[current['id']] - current['arrival_time']
                waiting_times[current['id']
                              ] = turnaround_times[current['id']] - current['burst_time']
        time += 1
    for p in processes:
        result.append({'id': p['id'], 'completion_time': completion_times[p['id']],
                      'waiting_time': waiting_times[p['id']], 'turnaround_time': turnaround_times[p['id']]})
    return result


def sjf_non_preemptive(processes):
    processes.sort(key=lambda x: x['burst_time'])
    time = 0
    result = []
    for process in processes:
        waiting_time = max(0, time)
        completion_time = time + process['burst_time']
        turnaround_time = completion_time
        result.append({'id': process['id'], 'completion_time': completion_time,
                      'waiting_time': waiting_time, 'turnaround_time': turnaround_time})
        time = completion_time
    return result


def round_robin2(processes, quantum):
    """Round Robin: Execute processes in time slices"""
    queue = sorted(processes, key=lambda x: x["arrival"])
    time = 0
    result = []
    waiting = queue[:]

    while waiting:
        process = waiting.pop(0)
        if time < process["arrival"]:
            time = process["arrival"]

        # Execute for quantum time or until complete
        execution_time = min(process["burst"], quantum)
        start_time = time
        time += execution_time
        process["burst"] -= execution_time

        result.append(
            {"pid": process["pid"], "start": start_time, "end": time})

        if process["burst"] > 0:
            waiting.append(process)
    return result


def round_robin(processes, quantum):
    queue = deque(processes)
    time = 0
    result = []
    waiting_times = {p['id']: 0 for p in processes}
    turnaround_times = {}
    while queue:
        process = queue.popleft()
        if process['burst_time'] > quantum:
            time += quantum
            process['burst_time'] -= quantum
            queue.append(process)
        else:
            time += process['burst_time']
            turnaround_times[process['id']] = time
            waiting_times[process['id']
                          ] = turnaround_times[process['id']] - process['burst_time']
            result.append({'id': process['id'], 'completion_time': time,
                          'waiting_time': waiting_times[process['id']], 'turnaround_time': turnaround_times[process['id']]})
    return result


def round_robin3(processes, quantum):
    """Round Robin: Execute processes in time slices"""
    # Initialize variables
    time = 0
    result = []
    waiting = processes[:]  # Copy the processes list

    # Continue processing until there are no processes left to handle
    while waiting:
        process = waiting.pop(0)

        # Execute the process for quantum time or until complete
        execution_time = min(process["burst_time"], quantum)
        start_time = time
        time += execution_time
        process["burst_time"] -= execution_time

        # Record the process execution details
        result.append(
            {"pid": process["id"], "start": start_time, "end": time}
        )

        # If the process is not completed, add it back to the waiting list
        if process["burst_time"] > 0:
            waiting.append(process)

    return result


def priority_preemptive(processes):
    processes.sort(key=lambda x: (x['arrival_time'], x['Priority']))
    time = 0
    result = []
    remaining_time = {p['id']: p['burst_time'] for p in processes}
    completion_times = {}
    waiting_times = {}
    turnaround_times = {}
    completed = 0
    while completed < len(processes):
        available_processes = [
            p for p in processes if p['arrival_time'] <= time and remaining_time[p['id']] > 0]
        if available_processes:
            current = min(available_processes, key=lambda x: x['Priority'])
            remaining_time[current['id']] -= 1
            if remaining_time[current['id']] == 0:
                completed += 1
                completion_times[current['id']] = time + 1
                turnaround_times[current['id']
                                 ] = completion_times[current['id']] - current['arrival_time']
                waiting_times[current['id']
                              ] = turnaround_times[current['id']] - current['burst_time']
        time += 1
    for p in processes:
        result.append({'id': p['id'], 'completion_time': completion_times[p['id']],
                      'waiting_time': waiting_times[p['id']], 'turnaround_time': turnaround_times[p['id']]})
    return result


def priority_non_preemptive(processes):
    processes.sort(key=lambda x: x['Priority'])
    time = 0
    result = []
    for process in processes:
        waiting_time = max(0, time)
        completion_time = time + process['burst_time']
        turnaround_time = completion_time
        result.append({'id': process['id'], 'completion_time': completion_time,
                      'waiting_time': waiting_time, 'turnaround_time': turnaround_time})
        time = completion_time
    return result


class ProcessDataView(APIView):
    def post(self, request, *args, **kwargs):

        if request.method == "POST":
            algorithm = request.data.get("algorithm")
            quantum = request.data.get("quantum")
            data = request.data.get("input_data")
            results = []
            if algorithm == "sjfp":
                results = sjf_preemptive(data)
            elif algorithm == "psp":
                results = priority_preemptive(data)
            elif algorithm == "psnp":
                results = priority_non_preemptive(data)
            elif algorithm == "rr":
                results = round_robin3(data, quantum)
            elif algorithm == "fcfs":
                results = fcfs(data)
            elif algorithm == "sjfnp":
                results = sjf_non_preemptive(data)
            print(results)
            print(algorithm)
        return Response(results)
