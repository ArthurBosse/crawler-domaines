/*
  # Mise à jour complète des politiques RLS pour la table domaines

  1. Modifications
    - Ajout de politiques pour toutes les opérations CRUD
    - Simplification des conditions de vérification

  2. Sécurité
    - Maintien de RLS activé
    - Accès complet pour les utilisateurs authentifiés
*/

-- Suppression des politiques existantes
DROP POLICY IF EXISTS "Enable insert for authenticated users" ON domaines;
DROP POLICY IF EXISTS "Enable read access for authenticated users" ON domaines;

-- Création des nouvelles politiques plus permissives
CREATE POLICY "Allow all operations for authenticated users"
    ON domaines
    FOR ALL
    TO authenticated
    USING (true)
    WITH CHECK (true);