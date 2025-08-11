-- Script para adicionar a coluna temporario na tabela conversations
-- Execute este script se a tabela já existir

-- Adicionar coluna temporario se não existir
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'conversations' 
        AND column_name = 'temporario'
    ) THEN
        ALTER TABLE conversations ADD COLUMN temporario BOOLEAN DEFAULT FALSE NOT NULL;
        RAISE NOTICE 'Coluna temporario adicionada com sucesso';
    ELSE
        RAISE NOTICE 'Coluna temporario já existe';
    END IF;
END $$;

-- Atualizar conversas existentes para definir temporario = false
-- (assumindo que conversas existentes têm user_id)
UPDATE conversations 
SET temporario = false 
WHERE user_id IS NOT NULL;

-- Definir temporario = true para conversas sem user_id (se houver)
UPDATE conversations 
SET temporario = true 
WHERE user_id IS NULL;

-- Verificar o resultado
SELECT 
    id, 
    user_id, 
    title, 
    temporario, 
    created_at 
FROM conversations 
ORDER BY created_at DESC 
LIMIT 10; 