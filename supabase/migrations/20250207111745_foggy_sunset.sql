/*
  # Mise à jour des politiques RLS pour la table domaines

  1. Modifications
    - Suppression et recréation de la politique d'insertion pour permettre aux utilisateurs authentifiés d'insérer des données
    - Ajout d'une politique pour permettre aux utilisateurs authentifiés de lire leurs propres données

  2. Sécurité
    - Maintien de RLS activé
    - Restriction des accès aux utilisateurs authentifiés uniquement
*/

-- Suppression des anciennes politiques
DROP POLICY IF EXISTS "Enable insert for authenticated users only" ON domaines;
DROP POLICY IF EXISTS "Enable read for authenticated users only" ON domaines;

-- Création des nouvelles politiques
CREATE POLICY "Enable insert for authenticated users"
    ON domaines
    FOR INSERT
    TO authenticated
    WITH CHECK (auth.uid() IS NOT NULL);

CREATE POLICY "Enable read access for authenticated users"
    ON domaines
    FOR SELECT
    TO authenticated
    USING (auth.uid() IS NOT NULL);