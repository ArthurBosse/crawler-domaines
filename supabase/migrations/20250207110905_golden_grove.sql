/*
  # Création de la table domaines et configuration RLS

  1. Nouvelle Table
    - `domaines`
      - `id` (uuid, clé primaire)
      - `url_source` (text)
      - `domaine_externe` (text)
      - `status_http` (text)
      - `statut_dns` (text)
      - `date_scan` (timestamp with time zone)
      - `created_at` (timestamp with time zone)

  2. Sécurité
    - Active RLS sur la table `domaines`
    - Ajoute une politique permettant l'insertion pour les utilisateurs authentifiés
    - Ajoute une politique permettant la lecture pour les utilisateurs authentifiés
*/

-- Création de la table si elle n'existe pas
CREATE TABLE IF NOT EXISTS domaines (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    url_source text NOT NULL,
    domaine_externe text NOT NULL,
    status_http text,
    statut_dns text,
    date_scan timestamptz NOT NULL,
    created_at timestamptz DEFAULT now()
);

-- Active RLS
ALTER TABLE domaines ENABLE ROW LEVEL SECURITY;

-- Politique pour permettre l'insertion à tous les utilisateurs authentifiés
CREATE POLICY "Enable insert for authenticated users only"
    ON domaines
    FOR INSERT
    TO authenticated
    WITH CHECK (true);

-- Politique pour permettre la lecture à tous les utilisateurs authentifiés
CREATE POLICY "Enable read for authenticated users only"
    ON domaines
    FOR SELECT
    TO authenticated
    USING (true);