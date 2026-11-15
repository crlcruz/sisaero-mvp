import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import hashlib

# ==============================================================================
# CONFIGURAÇÃO DA PÁGINA E IDENTIDADE VISUAL (SIS-AERO)
# ==============================================================================
st.set_page_config(
    page_title="SIS-AERO | Governance & Compliance UAS",
    page_icon="🚁",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo customizado para badges e cartões de protocolo
st.markdown("""
<style>
    .protocol-box {
        border: 2px solid #1E3A8A;
        border-radius: 10px;
        padding: 20px;
        background-color: #F8FAFC;
        color: #0F172A;
    }
    .alert-box {
        border-left: 5px solid #DC2626;
        background-color: #FEF2F2;
        padding: 12px;
        border-radius: 4px;
        color: #7F1D1D;
        font-size: 0.9rem;
    }
    .status-badge-ok {
        background-color: #DCFCE7;
        color: #166534;
        padding: 4px 10px;
        border-radius: 12px;
        font-weight: bold;
        font-size: 0.85rem;
    }
    .status-badge-warn {
        background-color: #FEF9C3;
        color: #854D0E;
        padding: 4px 10px;
        border-radius: 12px;
        font-weight: bold;
        font-size: 0.85rem;
    }
    .status-badge-err {
        background-color: #FEE2E2;
        color: #991B1B;
        padding: 4px 10px;
        border-radius: 12px;
        font-weight: bold;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# INICIALIZAÇÃO DO BANCO DE DADOS EM MEMÓRIA (SESSION STATE)
# ==============================================================================
def init_db():
    if "empresas" not in st.session_state:
        st.session_state.empresas = [
            {
                "id": "EMP-01",
                "razao_social": "Indústria Beta S.A.",
                "cnpj": "12.345.678/0001-90",
                "tipo": "Empresa Contratante",
                "responsavel": "Carlos Mendes",
                "contato_emergencia": "(85) 99999-1111"
            },
            {
                "id": "EMP-02",
                "razao_social": "Aerotech Operações Aéreas Ltda",
                "cnpj": "98.765.432/0001-10",
                "tipo": "Empresa Contratada",
                "responsavel": "Jano Faustino",
                "contato_emergencia": "(85) 98888-2222"
            }
        ]

    if "pilotos" not in st.session_state:
        st.session_state.pilotos = [
            {
                "id": "PIL-01",
                "nome": "João Silva",
                "cpf": "111.222.333-44",
                "empresa": "Aerotech Operações Aéreas Ltda",
                "qualificacao": "Piloto Remoto Comercial - RBAC 100",
                "cadastro_anac": "BR-PIL-998877",
                "situacao": "Regular"
            },
            {
                "id": "PIL-02",
                "nome": "Mariana Costa",
                "cpf": "555.666.777-88",
                "empresa": "Aerotech Operações Aéreas Ltda",
                "qualificacao": "Piloto Remoto - Operação VLOS",
                "cadastro_anac": "BR-PIL-445566",
                "situacao": "Pendente"
            }
        ]

    if "drones" not in st.session_state:
        st.session_state.drones = [
            {
                "id": "UAS-01",
                "fabricante": "DJI",
                "modelo": "Matrice 4TD",
                "numero_serie": "1581F67G24001A",
                "mtow_kg": 4.2,
                "categoria": "Classe 3 (250g a 25kg)",
                "tipo_operacao": "VLOS",
                "cadastro_anac": "PP-01020304",
                "homologacao_anatel": "12345-24-07248",
                "empresa_proprietaria": "Aerotech Operações Aéreas Ltda",
                "manutencao": "Em dia"
            }
        ]

    if "locais" not in st.session_state:
        st.session_state.locais = [
            {
                "id": "LOC-01",
                "nome": "Planta Industrial Distrito Norte",
                "municipio": "Fortaleza",
                "uf": "CE",
                "coordenadas": "-3.7319, -38.5267",
                "altitude_m": 120,
                "ambiente": "Industrial",
                "pessoas_nao_envolvidas": "Não",
                "proximidade_aerodromo": "Fora da ZPA ( > 9 km )"
            }
        ]

    if "documentos" not in st.session_state:
        hoje = date.today()
        st.session_state.documentos = [
            {
                "doc_id": "DOC-101",
                "tipo_documento": "Certificado de Cadastro ANAC (SISANT)",
                "vinculo_tipo": "Aeronave",
                "vinculo_nome": "DJI Matrice 4TD (PP-01020304)",
                "orgao_emissor": "ANAC",
                "identificador": "SISANT-2026-8841",
                "emissao": str(hoje - timedelta(days=300)),
                "validade": str(hoje + timedelta(days=65)),
                "status_conferencia": "Conferido"
            },
            {
                "doc_id": "DOC-102",
                "tipo_documento": "Homologação ANATEL",
                "vinculo_tipo": "Aeronave",
                "vinculo_nome": "DJI Matrice 4TD (PP-01020304)",
                "orgao_emissor": "ANATEL",
                "identificador": "12345-24-07248",
                "emissao": str(hoje - timedelta(days=400)),
                "validade": str(hoje + timedelta(days=12)),  # Próximo do vencimento (< 15 dias)
                "status_conferencia": "Conferido"
            },
            {
                "doc_id": "DOC-103",
                "tipo_documento": "Seguro RETA / Responsabilidade Civil",
                "vinculo_tipo": "Empresa",
                "vinculo_nome": "Aerotech Operações Aéreas Ltda",
                "orgao_emissor": "Seguradora Aero",
                "identificador": "APOL-99102",
                "emissao": str(hoje - timedelta(days=370)),
                "validade": str(hoje - timedelta(days=5)),  # Vencido
                "status_conferencia": "Pendente Atualização"
            },
            {
                "doc_id": "DOC-104",
                "tipo_documento": "Autorização de Acesso ao Espaço Aéreo (SARPAS)",
                "vinculo_tipo": "Operação",
                "vinculo_nome": "ITA-UAS-2026-000125",
                "orgao_emissor": "DECEA",
                "identificador": "SARPAS-BR-77412",
                "emissao": str(hoje),
                "validade": str(hoje + timedelta(days=2)),
                "status_conferencia": "Aguardando Conferência"
            }
        ]

    if "operacoes" not in st.session_state:
        st.session_state.operacoes = [
            {
                "protocolo": "ITA-UAS-2026-000125",
                "contratante": "Indústria Beta S.A.",
                "operador": "Aerotech Operações Aéreas Ltda",
                "piloto": "João Silva",
                "aeronave": "DJI Matrice 4TD",
                "local": "Planta Industrial Distrito Norte",
                "data_voo": "2026-11-20",
                "horario": "08:00 - 10:00",
                "tipo_voo": "VLOS",
                "finalidade": "Inspeção patrimonial",
                "validacao_documental": "Documentação conferida",
                "verificacao_regulatoria": "Aguardando confirmação DECEA (ICA 100-40)",
                "status_operacao": "Requisitos documentais conferidos",
                "historico": [
                    f"{datetime.now().strftime('%d/%m/%Y %H:%M')} - Solicitação registrada no sistema.",
                    f"{datetime.now().strftime('%d/%m/%Y %H:%M')} - Matriz documental vinculada automaticamente."
                ]
            }
        ]

init_db()

# ==============================================================================
# FUNÇÕES AUXILIARES DE GOVERNANÇA E VALIDAÇÃO
# ==============================================================================
def calcular_status_validade(validade_str):
    validade = datetime.strptime(validade_str, "%Y-%m-%d").date()
    dias_restantes = (validade - date.today()).days
    if dias_restantes < 0:
        return f"Vencido ({abs(dias_restantes)}d atrás)", "err"
    elif dias_restantes <= 7:
        return f"Crítico: Vence em {dias_restantes}d", "err"
    elif dias_restantes <= 15:
        return f"Alerta: Vence em {dias_restantes}d", "warn"
    elif dias_restantes <= 30:
        return f"Atenção: Vence em {dias_restantes}d", "warn"
    else:
        return f"Válido ({dias_restantes}d)", "ok"

def gerar_url_qr_code(protocolo):
    # Gera uma URL de QR Code público para validação visual do protocolo
    dados = f"https://sisaero.gov.br/consulta/{protocolo}"
    return f"https://api.qrserver.com/v1/create-qr-code/?size=160x160&data={dados}"

# ==============================================================================
# BARRA LATERAL: AMBIENTE INSTITUCIONAL E NAVEGAÇÃO
# ==============================================================================
with st.sidebar:
    st.title("🚁 SIS-AERO")
    st.caption("Sistema Integrado de Segurança, Cadastro e Rastreabilidade de Operações com RPA/UAS")
    st.divider()

    # Modelo de utilização institucional (Seção 8 e 14 do documento)
    perfil_acesso = st.selectbox(
        "Perfil de Acesso Institucional",
        [
            "Administrador do Sistema",
            "SIS-AERO Governo (Prefeitura / Sec. Segurança)",
            "SIS-AERO Empresarial (Contratante / Operador)",
            "SIS-AERO Fiscalização (Agente / ANAC / DECEA)"
        ]
    )

    st.info(f"**Ambiente Ativo:**\n{perfil_acesso}")
    st.divider()

    menu = st.radio(
        "Módulos da Plataforma",
        [
            "1. Dashboard & Painel Municipal",
            "2. Cadastros Base (Entidades)",
            "3. Análise Documental & Compliance",
            "4. Solicitação & Liberação de Voo",
            "5. Fiscalização & Consulta QR Code"
        ]
    )

    st.divider()
    st.caption("Conformidade: LGPD • RBAC 100 • ICA 100-40 • ISO 27001")

# ==============================================================================
# MÓDULO 1: DASHBOARD & PAINEL DE CONTROLE MUNICIPAL
# ==============================================================================
if menu == "1. Dashboard & Painel Municipal":
    st.header("📊 Painel Central de Governança — SIS-AERO")
    st.markdown("Monitoramento consolidado de operações aéreas, conformidade documental e rastreabilidade municipal.")

    # Métricas Principais
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Aeronaves Cadastradas", len(st.session_state.drones))
    col2.metric("Pilotos Remotos", len(st.session_state.pilotos))
    col3.metric("Empresas Vinculadas", len(st.session_state.empresas))
    col4.metric("Operações Registradas", len(st.session_state.operacoes))

    st.divider()

    col_left, col_right = st.columns([1.2, 1])

    with col_left:
        st.subheader("📋 Situação das Solicitações de Operação")
        df_ops = pd.DataFrame(st.session_state.operacoes)
        if not df_ops.empty:
            st.dataframe(
                df_ops[["protocolo", "operador", "piloto", "aeronave", "data_voo", "status_operacao"]],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("Nenhuma operação registrada.")

    with col_right:
        st.subheader("🛡️ Indicadores de Conformidade Documental")
        docs_validos = 0
        docs_alerta = 0
        docs_vencidos = 0

        for d in st.session_state.documentos:
            _, nivel = calcular_status_validade(d["validade"])
            if nivel == "ok":
                docs_validos += 1
            elif nivel == "warn":
                docs_alerta += 1
            else:
                docs_vencidos += 1

        c1, c2, c3 = st.columns(3)
        c1.metric("Documentos Válidos", docs_validos)
        c2.metric("Próx. Vencimento", docs_alerta)
        c3.metric("Vencidos / Críticos", docs_vencidos)

        # Gráfico simples de distribuição
        chart_data = pd.DataFrame({
            "Status": ["Válidos", "Próximos do Vencimento", "Vencidos/Críticos"],
            "Quantidade": [docs_validos, docs_alerta, docs_vencidos]
        }).set_index("Status")
        st.bar_chart(chart_data)

# ==============================================================================
# MÓDULO 2: CADASTROS BASE (PILOTOS, DRONES, EMPRESAS E LOCAIS)
# ==============================================================================
elif menu == "2. Cadastros Base (Entidades)":
    st.header("🗂️ Cadastros Independentes do Ecossistema")
    st.markdown("Os cadastros são independentes e vinculados automaticamente durante a solicitação de voo.")

    tab_piloto, tab_drone, tab_empresa, tab_local = st.tabs([
        "👨‍✈️ Pilotos Remotos",
        "🛸 Vetores Aéreos (Drones)",
        "🏢 Empresas (Contratante/Contratada)",
        "📍 Locais de Voo"
    ])

    # --- ABA PILOTOS ---
    with tab_piloto:
        st.subheader("Cadastrar Novo Piloto Remoto")
        with st.form("form_piloto", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            nome_p = c1.text_input("Nome Completo*")
            cpf_p = c2.text_input("CPF*")
            anac_p = c3.text_input("Cadastro ANAC*")

            c4, c5, c6 = st.columns(3)
            emp_p = c4.selectbox("Empresa Vinculada", [e["razao_social"] for e in st.session_state.empresas])
            qual_p = c5.text_input("Qualificação / Formação", value="Piloto Remoto - RBAC 100")
            sit_p = c6.selectbox("Situação Cadastral", ["Regular", "Pendente", "Vencido"])

            if st.form_submit_button("Salvar Piloto"):
                if nome_p and cpf_p and anac_p:
                    st.session_state.pilotos.append({
                        "id": f"PIL-0{len(st.session_state.pilotos)+1}",
                        "nome": nome_p,
                        "cpf": cpf_p,
                        "empresa": emp_p,
                        "qualificacao": qual_p,
                        "cadastro_anac": anac_p,
                        "situacao": sit_p
                    })
                    st.success(f"Piloto {nome_p} cadastrado com sucesso!")
                else:
                    st.error("Preencha os campos obrigatórios (*).")

        st.subheader("Pilotos Cadastrados")
        st.dataframe(pd.DataFrame(st.session_state.pilotos), use_container_width=True, hide_index=True)

    # --- ABA DRONES ---
    with tab_drone:
        st.subheader("Cadastrar Nova Aeronave (RPA/UAS)")
        with st.form("form_drone", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            fab_d = c1.text_input("Fabricante*", placeholder="Ex: DJI, Autel")
            mod_d = c2.text_input("Modelo*", placeholder="Ex: Matrice 350 RTK")
            sn_d = c3.text_input("Número de Série*")

            c4, c5, c6 = st.columns(3)
            mtow_d = c4.number_input("Peso Máximo Decolagem - MTOW (kg)", min_value=0.1, value=2.5)
            cat_d = c5.selectbox("Categoria Operacional (RBAC)", ["Classe 3 (250g a 25kg)", "Classe 2 (25kg a 150kg)", "Classe 1 (> 150kg)"])
            op_d = c6.selectbox("Tipo de Operação", ["VLOS", "EVLOS", "BVLOS"])

            c7, c8, c9 = st.columns(3)
            anac_d = c7.text_input("Registro ANAC (SISANT)*")
            anatel_d = c8.text_input("Homologação ANATEL*")
            prop_d = c9.selectbox("Empresa Proprietária", [e["razao_social"] for e in st.session_state.empresas])

            if st.form_submit_button("Salvar Aeronave"):
                if fab_d and mod_d and sn_d and anac_d:
                    st.session_state.drones.append({
                        "id": f"UAS-0{len(st.session_state.drones)+1}",
                        "fabricante": fab_d,
                        "modelo": mod_d,
                        "numero_serie": sn_d,
                        "mtow_kg": mtow_d,
                        "categoria": cat_d,
                        "tipo_operacao": op_d,
                        "cadastro_anac": anac_d,
                        "homologacao_anatel": anatel_d,
                        "empresa_proprietaria": prop_d,
                        "manutencao": "Em dia"
                    })
                    st.success(f"Aeronave {fab_d} {mod_d} cadastrada com sucesso!")
                else:
                    st.error("Preencha os campos obrigatórios (*).")

        st.subheader("Inventário de Aeronaves")
        st.dataframe(pd.DataFrame(st.session_state.drones), use_container_width=True, hide_index=True)

    # --- ABA EMPRESAS ---
    with tab_empresa:
        st.subheader("Cadastrar Empresa (Contratante ou Contratada)")
        with st.form("form_empresa", clear_on_submit=True):
            c1, c2 = st.columns(2)
            rz_e = c1.text_input("Razão Social*")
            cnpj_e = c2.text_input("CNPJ*")

            c3, c4, c5 = st.columns(3)
            tipo_e = c3.selectbox("Perfil Empresarial", ["Empresa Contratante", "Empresa Contratada", "Subcontratada"])
            resp_e = c4.text_input("Responsável Técnico / Legal*")
            tel_e = c5.text_input("Contato de Emergência*")

            if st.form_submit_button("Salvar Empresa"):
                if rz_e and cnpj_e:
                    st.session_state.empresas.append({
                        "id": f"EMP-0{len(st.session_state.empresas)+1}",
                        "razao_social": rz_e,
                        "cnpj": cnpj_e,
                        "tipo": tipo_e,
                        "responsavel": resp_e,
                        "contato_emergencia": tel_e
                    })
                    st.success(f"Empresa {rz_e} cadastrada com sucesso!")
                else:
                    st.error("Razão Social e CNPJ são obrigatórios.")

        st.subheader("Empresas Registradas")
        st.dataframe(pd.DataFrame(st.session_state.empresas), use_container_width=True, hide_index=True)

    # --- ABA LOCAIS ---
    with tab_local:
        st.subheader("Cadastrar Área Operacional / Local de Voo")
        with st.form("form_local", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            nome_l = c1.text_input("Nome da Instalação / Empreendimento*")
            mun_l = c2.text_input("Município*", value="Fortaleza")
            uf_l = c3.text_input("UF*", value="CE")

            c4, c5, c6 = st.columns(3)
            coord_l = c4.text_input("Coordenadas Geográficas (Lat, Lon)*", value="-3.7450, -38.5120")
            alt_l = c5.number_input("Altitude / Altura Pretendida (m)", min_value=10, max_value=400, value=120)
            amb_l = c6.selectbox("Tipo de Ambiente", ["Urbano", "Industrial", "Rural", "Infraestrutura Crítica"])

            c7, c8 = st.columns(2)
            pess_l = c7.selectbox("Existência de pessoas não envolvidas?", ["Não", "Sim (requer análise de risco específica)"])
            aero_l = c8.text_input("Proximidade de Aeródromos / Restrições", value="Fora de área restrita")

            if st.form_submit_button("Salvar Local de Voo"):
                if nome_l and coord_l:
                    st.session_state.locais.append({
                        "id": f"LOC-0{len(st.session_state.locais)+1}",
                        "nome": nome_l,
                        "municipio": mun_l,
                        "uf": uf_l,
                        "coordenadas": coord_l,
                        "altitude_m": alt_l,
                        "ambiente": amb_l,
                        "pessoas_nao_envolvidas": pess_l,
                        "proximidade_aerodromo": aero_l
                    })
                    st.success(f"Local '{nome_l}' cadastrado! Lembrete: o cadastro não substitui consulta DECEA.")
                else:
                    st.error("Preencha o nome do local e as coordenadas.")

        st.subheader("Locais Cadastrados")
        st.dataframe(pd.DataFrame(st.session_state.locais), use_container_width=True, hide_index=True)

# ==============================================================================
# MÓDULO 3: ANÁLISE DOCUMENTAL & MATRIZ DE COMPLIANCE
# ==============================================================================
elif menu == "3. Análise Documental & Compliance":
    st.header("📑 Matriz Documental Inteligente & Compliance Regulatório")
    st.markdown("Controle de evidências vinculadas a pilotos, aeronaves, empresas e operações, com alertas automáticos de vencimento (30, 15, 7 dias).")

    col_upload, col_lista = st.columns([1, 1.6])

    with col_upload:
        st.subheader("📤 Anexar Novo Documento")
        with st.form("form_doc", clear_on_submit=True):
            tipo_doc = st.selectbox("Tipo de Documento / Requisito", [
                "Certificado de Cadastro ANAC (SISANT)",
                "Homologação ANATEL",
                "Autorização de Acesso ao Espaço Aéreo (DECEA / SARPAS)",
                "Seguro RETA / Responsabilidade Civil",
                "Avaliação de Risco Operacional (SORA)",
                "Manual de Operações",
                "Plano de Emergência",
                "Avaliação de Impacto LGPD"
            ])
            vinc_tipo = st.selectbox("Vincular a", ["Aeronave", "Piloto", "Empresa", "Operação"])
            vinc_nome = st.text_input("Identificação do Vínculo*", placeholder="Ex: DJI Matrice 4TD ou João Silva")
            orgao = st.text_input("Órgão Emissor*", placeholder="Ex: ANAC, DECEA, ANATEL")
            ident = st.text_input("Número / Identificador Documental*")
            dt_emissao = st.date_input("Data de Emissão", value=date.today())
            dt_validade = st.date_input("Data de Validade", value=date.today() + timedelta(days=180))
            arquivo = st.file_uploader("Arquivo Digital (PDF, PNG, JPG)", type=["pdf", "png", "jpg"])

            if st.form_submit_button("Registrar Documento"):
                if vinc_nome and ident:
                    st.session_state.documentos.append({
                        "doc_id": f"DOC-{100 + len(st.session_state.documentos) + 1}",
                        "tipo_documento": tipo_doc,
                        "vinculo_tipo": vinc_tipo,
                        "vinculo_nome": vinc_nome,
                        "orgao_emissor": orgao,
                        "identificador": ident,
                        "emissao": str(dt_emissao),
                        "validade": str(dt_validade),
                        "status_conferencia": "Aguardando Conferência"
                    })
                    st.success("Documento anexado e registrado na trilha de auditoria!")
                else:
                    st.error("Informe o vínculo e o identificador do documento.")

    with col_lista:
        st.subheader("🔍 Conferência e Alertas de Vigência")
        for idx, doc in enumerate(st.session_state.documentos):
            texto_val, nivel = calcular_status_validade(doc["validade"])
            with st.expander(f"{doc['doc_id']} | {doc['tipo_documento']} — [{texto_val}]", expanded=(nivel != "ok")):
                c1, c2 = st.columns(2)
                c1.write(f"**Vínculo ({doc['vinculo_tipo']}):** {doc['vinculo_nome']}")
                c1.write(f"**Órgão Emissor:** {doc['orgao_emissor']}")
                c2.write(f"**Identificador:** `{doc['identificador']}`")
                c2.write(f"**Validade:** {doc['validade']} | **Status:** {doc['status_conferencia']}")

                # Ação de conferência documental (exclusiva para perfis autorizados)
                if perfil_acesso != "SIS-AERO Empresarial (Contratante / Operador)":
                    col_b1, col_b2 = st.columns(2)
                    if col_b1.button("✅ Validar Conferência", key=f"val_{idx}"):
                        st.session_state.documentos[idx]["status_conferencia"] = "Conferido"
                        st.rerun()
                    if col_b2.button("⚠️ Marcar Pendência", key=f"pend_{idx}"):
                        st.session_state.documentos[idx]["status_conferencia"] = "Pendente / Irregular"
                        st.rerun()

# ==============================================================================
# MÓDULO 4: SOLICITAÇÃO E LIBERAÇÃO DE OPERAÇÕES (CORAÇÃO DO SIS-AERO)
# ==============================================================================
elif menu == "4. Solicitação & Liberação de Voo":
    st.header("🛫 Solicitação Digital e Fluxo de Liberação de Voo")

    st.markdown("""
    <div class="alert-box">
        <strong>Princípio de Governança SIS-AERO:</strong> A plataforma diferencia <em>Validação Documental</em>, 
        <em>Verificação Regulatória</em> e <em>Liberação Operacional</em>. O protocolo gerado <strong>não substitui</strong> 
        autorização de voo da ANAC ou acesso ao espaço aéreo pelo DECEA (ICA 100-40).
    </div>
    """, unsafe_allow_html=True)
    st.write("")

    col_form, col_fluxo = st.columns([1.1, 1])

    with col_form:
        st.subheader("1. Nova Solicitação de Operação")
        with st.form("form_solicitacao"):
            contratante = st.selectbox("Empresa Contratante", [e["razao_social"] for e in st.session_state.empresas])
            operador = st.selectbox("Empresa Operadora (Contratada)", [e["razao_social"] for e in st.session_state.empresas], index=min(1, len(st.session_state.empresas)-1))
            piloto_sel = st.selectbox("Piloto Remoto Designado", [p["nome"] for p in st.session_state.pilotos])
            drone_sel = st.selectbox("Aeronave (RPA/UAS)", [f"{d['fabricante']} {d['modelo']}" for d in st.session_state.drones])
            local_sel = st.selectbox("Local da Operação", [l["nome"] for l in st.session_state.locais])

            c1, c2 = st.columns(2)
            data_voo = c1.date_input("Data Prevista do Voo", value=date.today() + timedelta(days=5))
            horario_voo = c2.text_input("Janela de Horário", value="08:00 - 11:00")

            c3, c4 = st.columns(2)
            tipo_voo = c3.selectbox("Modalidade", ["VLOS", "EVLOS", "BVLOS"])
            finalidade = c4.text_input("Finalidade da Operação", value="Inspeção técnica")

            evidencia_decea = st.checkbox("Declaro que a consulta/autorização DECEA (SARPAS) foi anexada ou está em trâmite.")

            if st.form_submit_button("Gerar Solicitação e Protocolo Digital"):
                # Verificação automática de consistência do piloto selecionado
                piloto_obj = next((p for p in st.session_state.pilotos if p["nome"] == piloto_sel), None)
                sit_piloto = piloto_obj["situacao"] if piloto_obj else "Pendente"

                novo_num = 125 + len(st.session_state.operacoes)
                novo_protocolo = f"ITA-UAS-2026-{novo_num:06d}"

                status_doc = "Documentação conferida" if sit_piloto == "Regular" else "Pendência cadastral do piloto"
                status_reg = "Evidência DECEA informada" if evidencia_decea else "Aguardando evidência de autorização externa"
                status_geral = "Requisitos documentais conferidos" if (sit_piloto == "Regular" and evidencia_decea) else "Aguardando documentação"

                st.session_state.operacoes.append({
                    "protocolo": novo_protocolo,
                    "contratante": contratante,
                    "operador": operador,
                    "piloto": piloto_sel,
                    "aeronave": drone_sel,
                    "local": local_sel,
                    "data_voo": str(data_voo),
                    "horario": horario_voo,
                    "tipo_voo": tipo_voo,
                    "finalidade": finalidade,
                    "validacao_documental": status_doc,
                    "verificacao_regulatoria": status_reg,
                    "status_operacao": status_geral,
                    "historico": [
                        f"{datetime.now().strftime('%d/%m/%Y %H:%M')} - Solicitação criada por {perfil_acesso}.",
                        f"{datetime.now().strftime('%d/%m/%Y %H:%M')} - Checagem automática: Piloto ({sit_piloto})."
                    ]
                })
                st.success(f"Solicitação registrada! Protocolo gerado: **{novo_protocolo}**")

    with col_fluxo:
        st.subheader("2. Gestão de Estados e Liberação Operacional")
        if st.session_state.operacoes:
            op_escolhida = st.selectbox(
                "Selecione o Protocolo para Gerenciar Fluxo",
                [op["protocolo"] for op in st.session_state.operacoes]
            )
            idx_op = next(i for i, op in enumerate(st.session_state.operacoes) if op["protocolo"] == op_escolhida)
            op_atual = st.session_state.operacoes[idx_op]

            st.write(f"**Operador:** {op_atual['operador']} | **Piloto:** {op_atual['piloto']}")
            st.write(f"**Validação Documental:** {op_atual['validacao_documental']}")
            st.write(f"**Verificação Regulatória:** {op_atual['verificacao_regulatoria']}")
            st.info(f"**Estado Atual:** {op_atual['status_operacao']}")

            novo_estado = st.selectbox("Atualizar Estado da Operação", [
                "Em análise",
                "Aguardando evidência de autorização externa",
                "Requisitos documentais conferidos",
                "Aprovado pelo responsável operacional competente",
                "Operação em execução",
                "Operação encerrada",
                "Suspenso ou cancelado"
            ])

            if st.button("Registrar Mudança de Estado"):
                st.session_state.operacoes[idx_op]["status_operacao"] = novo_estado
                st.session_state.operacoes[idx_op]["historico"].append(
                    f"{datetime.now().strftime('%d/%m/%Y %H:%M')} - Estado alterado para '{novo_estado}' por {perfil_acesso}."
                )
                st.success("Estado atualizado na trilha de auditoria!")
                st.rerun()

            with st.expander("📜 Trilha de Auditoria da Operação"):
                for evento in op_atual["historico"]:
                    st.write(f"- {evento}")

# ==============================================================================
# MÓDULO 5: FISCALIZAÇÃO & CONSULTA POR QR CODE
# ==============================================================================
elif menu == "5. Fiscalização & Consulta QR Code":
    st.header("👮 Módulo de Fiscalização e Rastreabilidade por QR Code")
    st.markdown("Consulta controlada em campo por agentes públicos e autoridades competentes, respeitando a LGPD e as permissões do perfil.")

    protocolos_disp = [op["protocolo"] for op in st.session_state.operacoes]
    prot_consulta = st.selectbox("Digite ou selecione o Protocolo / Leitura QR Code", protocolos_disp)

    op = next((o for o in st.session_state.operacoes if o["protocolo"] == prot_consulta), None)

    if op:
        col_card, col_qr = st.columns([2, 1])

        with col_card:
            st.markdown(f"""
            <div class="protocol-box">
                <h3>PROTOCOLO DE OPERAÇÃO: {op['protocolo']}</h3>
                <hr>
                <p><strong>Operador (Contratada):</strong> {op['operador']}</p>
                <p><strong>Contratante:</strong> {op['contratante']}</p>
                <p><strong>Piloto Designado:</strong> {op['piloto']} <em>(CPF ocultado por conformidade LGPD)</em></p>
                <p><strong>Aeronave Utilizada:</strong> {op['aeronave']}</p>
                <p><strong>Local e Período:</strong> {op['local']} | {op['data_voo']} ({op['horario']})</p>
                <p><strong>Modalidade / Finalidade:</strong> {op['tipo_voo']} — {op['finalidade']}</p>
                <hr>
                <p><strong>Situação Documental:</strong> {op['validacao_documental']}</p>
                <p><strong>Evidência Regulatória:</strong> {op['verificacao_regulatoria']}</p>
                <p><strong>Status Operacional:</strong> <span class="status-badge-ok">{op['status_operacao']}</span></p>
            </div>
            """, unsafe_allow_html=True)

            st.write("")
            st.warning("⚠️ **Aviso Legal:** Este protocolo atesta apenas o registro e a conferência cadastral no SIS-AERO, não constituindo licença aeronáutica ou autorização de espaço aéreo.")

        with col_qr:
            st.subheader("Validação Rápida (Campo)")
            st.image(gerar_url_qr_code(op["protocolo"]), caption=f"QR Code: {op['protocolo']}")
            st.caption("Escaneie em campo para verificar autenticidade sem exposição de dados sensíveis.")

            if perfil_acesso in ["Administrador do Sistema", "SIS-AERO Fiscalização (Agente / ANAC / DECEA)"]:
                if st.button("🚨 Registrar Ocorrência / Notificação de Fiscalização"):
                    op["historico"].append(
                        f"{datetime.now().strftime('%d/%m/%Y %H:%M')} - Inspeção presencial registrada por {perfil_acesso}."
                    )
                    st.success("Registro de fiscalização gravado no histórico!")