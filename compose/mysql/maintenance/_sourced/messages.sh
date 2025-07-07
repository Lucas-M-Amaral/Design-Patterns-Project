#!/usr/bin/env bash


message_welcome() {
    echo ">>> $1"
}

message_info() {
    echo "INFO: $1"
}

message_success() {
    echo "SUCCESS: $1"
}

message_error() {
    echo "ERROR: $1" >&2
}
