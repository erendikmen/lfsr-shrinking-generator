library ieee;
use ieee.std_logic_1164.all;

entity tb_shrinking is
end entity;

architecture sim of tb_shrinking is
  -- Clock & reset
  signal clk       : std_logic := '0';
  signal rst_n     : std_logic := '0';

  -- Control & seeds
  signal en        : std_logic := '1';
  signal load_sel  : std_logic := '0';
  signal seed_sel  : std_logic_vector(30 downto 0) := (others => '1');
  signal load_dat  : std_logic := '0';
  signal seed_dat  : std_logic_vector(31 downto 0) := (others => '1');

  -- Outputs
  signal bit_o     : std_logic;
  signal valid_o   : std_logic;
  signal sel_q     : std_logic_vector(30 downto 0);
  signal dat_q     : std_logic_vector(31 downto 0);
begin
  -- 100 MHz clock (10 ns period)
  clk <= not clk after 5 ns;

  -- DUT
  dut: entity work.shrinking_generator
    port map(
      clk       => clk,
      rst_n     => rst_n,
      en        => en,
      load_sel  => load_sel,
      seed_sel  => seed_sel,
      load_dat  => load_dat,
      seed_dat  => seed_dat,
      bit_o     => bit_o,
      valid_o   => valid_o,
      sel_q     => sel_q,
      dat_q     => dat_q
    );

  -- Stimulus
  process
  begin
    -- Reset
    rst_n <= '0';
    wait for 50 ns;
    rst_n <= '1';

    -- Seeds yükle (1 clock)
    load_sel <= '1';
    load_dat <= '1';
    seed_sel <= (others => '1');       -- örnek non-zero seed
    seed_dat <= x"FFFFFFFF";           -- örnek non-zero seed
    wait for 10 ns;
    load_sel <= '0';
    load_dat <= '0';

    -- Koştur
    wait for 2 us;

    -- Bitir (xsim açık kalsın)
    assert false report "Simulation finished" severity note;
    wait;
  end process;
end architecture;
