noreplydev@machine $ uv run main.py ./Mistral-Nemo-Instruct-2407-Q3_K_L.gguf

── Model ────
Mistral-Nemo-Instruct-2407-Q3_K_L.gguf
────────────────────────
GGUF.version                           : 3
GGUF.tensor_count                      : 363
GGUF.kv_count                          : 40
general.architecture                   : llama
general.type                           : model
general.name                           : Mistral Nemo Instruct 2407
general.version                        : 2407
general.finetune                       : Instruct
general.basename                       : Mistral-Nemo
general.size_label                     : 12B
general.license                        : apache-2.0
general.base_model.count               : 1
general.base_model.0.name              : Mistral Nemo Base 2407
general.base_model.0.version           : 2407
general.base_model.0.organization      : Mistralai
general.base_model.0.repo_url          : https://huggingface.co/mistralai/Mistral-Nemo-Base-2407
general.languages                      : en
llama.block_count                      : 40
llama.context_length                   : 1024000
llama.embedding_length                 : 5120
llama.feed_forward_length              : 14336
llama.attention.head_count             : 32
llama.attention.head_count_kv          : 8
llama.rope.freq_base                   : 1000000.0
llama.attention.layer_norm_rms_epsilon : 9.999999747378752e-06
llama.attention.key_length             : 128
llama.attention.value_length           : 128
general.file_type                      : 13
llama.vocab_size                       : 131072
llama.rope.dimension_count             : 128
tokenizer.ggml.model                   : gpt2
tokenizer.ggml.pre                     : tekken
tokenizer.ggml.tokens                  : <unk>
tokenizer.ggml.token_type              : 3
tokenizer.ggml.merges                  : Ġ Ġ
tokenizer.ggml.bos_token_id            : 1
tokenizer.ggml.eos_token_id            : 2
tokenizer.ggml.unknown_token_id        : 0
tokenizer.ggml.add_bos_token           : True
tokenizer.ggml.add_eos_token           : False
tokenizer.chat_template                : {%- if messages[0]["role"] == "system" %}
    {%- set system_message = messages[0]["content"] %}
    {%- set loop_messages = messages[1:] %}
{%- else %}
    {%- set loop_messages = messages %}
{%- endif %}
{%- if not tools is defined %}
    {%- set tools = none %}
{%- endif %}
{%- set user_messages = loop_messages | selectattr("role", "equalto", "user") | list %}

{#- This block checks for alternating user/assistant messages, skipping tool calling messages #}
{%- set ns = namespace() %}
{%- set ns.index = 0 %}
{%- for message in loop_messages %}
    {%- if not (message.role == "tool" or message.role == "tool_results" or (message.tool_calls is defined and message.tool_calls is not none)) %}
        {%- if (message["role"] == "user") != (ns.index % 2 == 0) %}
            {{- raise_exception("After the optional system message, conversation roles must alternate user/assistant/user/assistant/...") }}
        {%- endif %}
        {%- set ns.index = ns.index + 1 %}
    {%- endif %}
{%- endfor %}

{{- bos_token }}
{%- for message in loop_messages %}
    {%- if message["role"] == "user" %}
        {%- if tools is not none and (message == user_messages[-1]) %}
            {{- "[AVAILABLE_TOOLS][" }}
            {%- for tool in tools %}
                {%- set tool = tool.function %}
                {{- '{"type": "function", "function": {' }}
                {%- for key, val in tool.items() if key != "return" %}
                    {%- if val is string %}
                        {{- '"' + key + '": "' + val + '"' }}
                    {%- else %}
                        {{- '"' + key + '": ' + val|tojson }}
                    {%- endif %}
                    {%- if not loop.last %}
                        {{- ", " }}
                    {%- endif %}
                {%- endfor %}
                {{- "}}" }}
                {%- if not loop.last %}
                    {{- ", " }}
                {%- else %}
                    {{- "]" }}
                {%- endif %}
            {%- endfor %}
            {{- "[/AVAILABLE_TOOLS]" }}
            {%- endif %}
        {%- if loop.last and system_message is defined %}
            {{- "[INST]" + system_message + "\n\n" + message["content"] + "[/INST]" }}
        {%- else %}
            {{- "[INST]" + message["content"] + "[/INST]" }}
        {%- endif %}
    {%- elif (message.tool_calls is defined and message.tool_calls is not none) %}
        {{- "[TOOL_CALLS][" }}
        {%- for tool_call in message.tool_calls %}
            {%- set out = tool_call.function|tojson %}
            {{- out[:-1] }}
            {%- if not tool_call.id is defined or tool_call.id|length != 9 %}
                {{- raise_exception("Tool call IDs should be alphanumeric strings with length 9!") }}
            {%- endif %}
            {{- ', "id": "' + tool_call.id + '"}' }}
            {%- if not loop.last %}
                {{- ", " }}
            {%- else %}
                {{- "]" + eos_token }}
            {%- endif %}
        {%- endfor %}
    {%- elif message["role"] == "assistant" %}
        {{- message["content"] + eos_token}}
    {%- elif message["role"] == "tool_results" or message["role"] == "tool" %}
        {%- if message.content is defined and message.content.content is defined %}
            {%- set content = message.content.content %}
        {%- else %}
            {%- set content = message.content %}
        {%- endif %}
        {{- '[TOOL_RESULTS]{"content": ' + content|string + ", " }}
        {%- if not message.tool_call_id is defined or message.tool_call_id|length != 9 %}
            {{- raise_exception("Tool call IDs should be alphanumeric strings with length 9!") }}
        {%- endif %}
        {{- '"call_id": "' + message.tool_call_id + '"}[/TOOL_RESULTS]' }}
    {%- else %}
        {{- raise_exception("Only user and assistant roles are supported, with the exception of an initial optional system message!") }}
    {%- endif %}
{%- endfor %}

tokenizer.ggml.add_space_prefix        : False
general.quantization_version           : 2