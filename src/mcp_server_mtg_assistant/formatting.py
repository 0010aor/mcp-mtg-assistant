from .schemas import ScryfallCard


def format_card_output(card_data: ScryfallCard) -> str:
    """Formats the Scryfall card data into a readable string."""
    formatted_output_parts = []

    if card_data.card_faces and len(card_data.card_faces) > 0:
        face_outputs = []
        for face in card_data.card_faces:
            face_name = face.name
            face_mana_cost = face.mana_cost or ''
            face_type_line = face.type_line or 'N/A'
            face_oracle_text = face.oracle_text or 'N/A'
            face_power = face.power
            face_toughness = face.toughness
            face_pt_line = f'P/T: {face_power}/{face_toughness}' if face_power and face_toughness else ''

            face_output = (
                f'{face_name} {face_mana_cost}\n'
                f'Type: {face_type_line}\n'
                f'{face_pt_line}\n'
                f'Oracle Text: {face_oracle_text}'.strip()
            )
            face_outputs.append(face_output)

        formatted_output_parts.append(' // '.join(face_outputs))
        cmc = card_data.cmc
        formatted_output_parts.append(f'\n(Overall CMC: {cmc})')

    else:
        name = card_data.name
        mana_cost = card_data.mana_cost or 'N/A'
        cmc = card_data.cmc
        type_line = card_data.type_line or 'N/A'
        oracle_text = card_data.oracle_text or 'N/A'
        power = card_data.power
        toughness = card_data.toughness
        pt_line = f'P/T: {power}/{toughness}' if power and toughness else ''

        single_face_output = (
            f'Card: {name}\n'
            f'Mana Cost: {mana_cost} (CMC: {cmc})\n'
            f'Type: {type_line}\n'
            f'{pt_line}\n'
            f'Oracle Text: {oracle_text}'
        )
        formatted_output_parts.append(single_face_output.strip())

    return ''.join(formatted_output_parts)
