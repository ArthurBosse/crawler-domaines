/*
  # Fix RLS policies for domaines table

  1. Changes
    - Disable RLS temporarily to debug the issue
    - Create a new comprehensive policy for authenticated users
    - Enable RLS with the new policy

  2. Security
    - Maintains security by requiring authentication
    - Allows all operations for authenticated users only
*/

-- Temporarily disable RLS to reset the policies
ALTER TABLE domaines DISABLE ROW LEVEL SECURITY;

-- Drop all existing policies to start fresh
DROP POLICY IF EXISTS "Allow all operations for authenticated users" ON domaines;
DROP POLICY IF EXISTS "Enable insert for authenticated users" ON domaines;
DROP POLICY IF EXISTS "Enable read access for authenticated users" ON domaines;

-- Create a single, comprehensive policy
CREATE POLICY "domaines_policy"
    ON domaines
    FOR ALL
    TO authenticated
    USING (true)
    WITH CHECK (true);

-- Re-enable RLS
ALTER TABLE domaines ENABLE ROW LEVEL SECURITY;