# Importação de bibliotecas
from transformers import AutoTokenizer, AutoModelForCausalLM # Pega de transformers o "tradutor/conversor" (AutoTokenizer) e o "cérebro" (AutoModelForCausalLM)
import torch # Pega a "estrutura matemática" que o torch oferece por meio de seus tensores


# Pré-carregamento do tokenizer e modelo para otimização de recursos computacionais
_TOK = None
_MODEL = None


# Função para chamar o modelo e configurá-lo
def carregar_modelo(
    model_id: str = "Qwen/Qwen2.5-1.5B-Instruct", # Define o modelo que vai ser utilizado
    prefer_gpu: bool = True # Indica a preferência pelo uso de GPU
):
    """
    -> Carrega e configura o modelo de IA, deixando-o pronto para uso
    :param model_id: Nome do modelo de IA que vai ser utilizado
    :param prefer_gpu: Para permitir o uso de GPU
    :return: Retorna o Tokenizer e o Modelo escolhido
    """
    # Verifica se o tokenizer e modelo já foram carregados, evitando que sejam recarregados desnecessariamente
    global _TOK, _MODEL
    if _TOK is not None and _MODEL is not None:
        return _TOK, _MODEL

    # Verifica se há CUDA, que permite o uso de GPU
    has_cuda = torch.cuda.is_available() and prefer_gpu
    if has_cuda:
        # Se uma GPU está disponível, utiliza metade da precisão e a atribuição automática de dispositivo
        dtype = torch.float16
        device_map="auto"
    else:
        # Caso contrário, utiliza precisão completa para operar na CPU (padrão)
        dtype = torch.float32
        device_map = None

    tok = AutoTokenizer.from_pretrained(model_id) # Guarda o "tradutor" do modelo

    # Tratamento de exceções para o processo de "guardar o cérebro" do modelo
    try:
        model = AutoModelForCausalLM.from_pretrained(
            model_id,
            torch_dtype=dtype,
            device_map=device_map,
            low_cpu_mem_usage=True
        )
    except Exception:
        model = AutoModelForCausalLM.from_pretrained(
            model_id,
            torch_dtype=torch.float32,
            device_map=None,
            low_cpu_mem_usage=True
        )

    model.eval() # Liga o modo de inferência do modelo
    _TOK, _MODEL = tok, model # Guarda o "idioma" e "cérebro" do modelo para evitar novo carregamento
    return tok, model # Retorna o "idioma" e o modelo configurado para a tarefa


# Função para encaminhar instruções para a recomendação de roupas personalizada pela previsão do tempo
def gerar_recomendacao(minima: str, maxima: str, condicao_clima: str) -> str:
    """
    -> Recebe as informações climáticas e as repassa ao modelo de IA para que ele gere recomendações de vestuário 
    :param minima: Temperatura mínima da cidade
    :param maxima: Temperatura máxima da cidade
    :param condicao_clima: Condição climática da cidade (ensolarado, chuvoso, nublado, etc)
    :return: Retorna recomendações de vestuário baseados no clima para os públicos masculino e feminino
    """
    tok, model = carregar_modelo() # Chama o modelo carregado para atuar dentro da função
    texto = [
        {"role": "system",
         "content": "Você é um consultor de moda especializado em recomendar roupas para previsão do tempo. Sua comunicaçao é em português, objetiva e prática. Use um tom casual e emojis. O formato de resposta deve ser EXATAMENTE o que é solicitado, sem desvios."},
        {"role": "user",
         "content": f"Com base nas seguintes informações de clima: Temperatura mínima de {minima}°C, máxima de {maxima}°C e condição {condicao_clima}."
                    "Sugira **apenas uma peça de vestuário** por categoria para o público masculino e feminino. A resposta deve seguir a formatação abaixo, sem adicionar ou remover nada: "
                    "\n\n**Público Masculino:**"
                    "\n- Parte Superior: [SUGESTÃO]"
                    "\n- Parte Inferior: [SUGESTÃO]"
                    "\n- Calçados: [SUGESTÃO]"
                    "\n- Acessórios: [SUGESTÃO]"
                    "\n\n**Público Feminino:**"
                    "\n- Parte Superior: [SUGESTÃO]"
                    "\n- Parte Inferior: [SUGESTÃO]"
                    "\n- Calçados: [SUGESTÃO]"
                    "\n- Acessórios: [SUGESTÃO]"
         }
    ]

    # Formata a entrada do usuário no estilo chat para que o modelo entenda, deixando um "aviso" sinalizando que ele já pode gerar a resposta
    prompt = tok.apply_chat_template(texto, tokenize=False, add_generation_prompt=True)
    # Converte o prompt para os tensores (tokenização) e o encaminha para a GPU/CPU que fornece os recursos de funcionamento do modelo
    inputs = tok(prompt, return_tensors="pt").to(model.device)

    # Gera a saída seguindo as instruções específicadas
    out = model.generate(
        **inputs,
        max_new_tokens=250,
        do_sample=True,
        temperature=0.2,
        top_p=0.8,
        repetition_penalty=1.3,
        eos_token_id=tok.eos_token_id
    )

    # Calcula o tamanho do input do usuário para então remover o conteúdo que ocupa tal espaço da resposta final, deixando-o a limpa
    comprimento_entrada = inputs["input_ids"].shape[-1]
    resposta = tok.decode(out[0][comprimento_entrada:], skip_special_tokens=True).strip()

    return resposta


# Verifica se o modelo está sendo corretamente carregado
if __name__ == "__main__":
    tok, model = carregar_modelo()
    print("Modelo carregado com sucesso.")
