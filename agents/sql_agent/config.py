# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
from dotenv import load_dotenv
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

load_dotenv()

TOOLBOX_HOST = os.getenv("TOOLBOX_HOST", "127.0.0.1")
TOOLBOX_PORT = os.getenv("TOOLBOX_PORT", "5000")
TOOLBOX_URL = f"http://{TOOLBOX_HOST}:{TOOLBOX_PORT}/mcp"

mcp_connection_params = StreamableHTTPConnectionParams(url=TOOLBOX_URL)
