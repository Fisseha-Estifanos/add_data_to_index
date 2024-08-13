import asyncio
from langchain_huggingface import HuggingFaceEmbeddings
from transformers import AutoTokenizer, AutoModel


async def get_hf_encoder(hf_encoder_name: str = "default"):
    try:
        if hf_encoder_name == "default":
            return AutoModel.from_pretrained("ncbi/MedCPT-Article-Encoder")
        embedding_model = HuggingFaceEmbeddings(
            model_name=hf_encoder_name,
            multi_process=True,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": False},  # Set `True` for cosine similarity
        )
        return embedding_model
    except Exception as ex:
        print("An error occurred while fetching hugging face encoder named "
              + f": {hf_encoder_name}.\nError : {ex}")


# wanted_model_name = "ncbi/MedCPT-Article-Encoder"
# embeddings =  asyncio.run(get_hf_encoder())
# # # Type : <class 'langchain_huggingface.embeddings.huggingface.HuggingFaceEmbeddings'>

# print((f"\t\tembeddings : {embeddings}\n\t\tType : {type(embeddings)}"))
# text = "This is a test document."
# query_result = embeddings.embed_query(text)
# print(f"query_result : {query_result[:5]}\nType : {type(query_result)}\nLength : {len(query_result)}")
# # # Type : <class 'list'>




# # # Load model directly
# # from transformers import AutoTokenizer, AutoModel

# # tokenizer = AutoTokenizer.from_pretrained("ncbi/MedCPT-Article-Encoder")
# # # # Type:<class 'transformers.models.bert.tokenization_bert_fast.BertTokenizerFast'>

# # model = AutoModel.from_pretrained("ncbi/MedCPT-Article-Encoder")
# # # Type:<class 'transformers.models.bert.modeling_bert.BertModel'>

# # print(f"tokenizer : {tokenizer}\nType:{type(tokenizer)}\n\n\n")
# # print(f"model : {model}\nType:{type(model)}")

# # text = "This is a test document."
# # inputs = tokenizer(text, return_tensors="pt")
# # outputs = model(**inputs)
# # print(f"outputs : {outputs}\nType : {type(outputs)}")
# # # Type : <class 'transformers.modeling_outputs.BaseModelOutputWithPoolingAndCrossAttentions'>

