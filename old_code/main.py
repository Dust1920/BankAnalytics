import universal_state as uni
import manager


# print(origin)
invex_test = r"Banks/INVEX/Credito/2025-07.pdf"
bbva_test = r"Banks/BBVA/Credito/BBVA Abril25.pdf"

origin = bbva_test
check = uni.is_universal(origin)

if check:
    pdf = manager.state_bank(origin)
    sample = manager.read_pages(pdf, [0, 1])
    bank = manager.find_bak(sample)

    state_sections, bank_state_blocks = uni.config_state_bank(origin)
    # print(state_sections)
    if 'DESGLOSE DE MOVIMIENTOS' in state_sections.keys():
        # print(universal_tests.loc[select_file, "filename"])
        exp_df, msi_df = uni.expenses_bbva(bank_state_blocks, bak=bank)
        msi_df.to_csv(f"A_MSI.csv")
        exp_df.to_csv(f"A_EXP.csv")
