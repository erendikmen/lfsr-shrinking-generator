library ieee;
use ieee.std_logic_1164.all;

entity shrinking_generator is
  port(
    clk       : in  std_logic;
    rst_n     : in  std_logic;
    en        : in  std_logic := '1';

    -- Selector (31-bit)
    load_sel  : in  std_logic := '0';
    seed_sel  : in  std_logic_vector(30 downto 0) := (others => '1');

    -- Selected/Data (32-bit)
    load_dat  : in  std_logic := '0';
    seed_dat  : in  std_logic_vector(31 downto 0) := (others => '1');

    -- Çıkış
    bit_o     : out std_logic;
    valid_o   : out std_logic;

    -- Debug (opsiyonel)
    sel_q     : out std_logic_vector(30 downto 0);
    dat_q     : out std_logic_vector(31 downto 0)
  );
end entity;

architecture rtl of shrinking_generator is
  signal sel_bit : std_logic;
  signal sel_q_s : std_logic_vector(30 downto 0);

  signal dat_bit : std_logic;
  signal dat_q_s : std_logic_vector(31 downto 0);
begin
  -- 31-bit selector
  u_sel: entity work.lfsr31
    port map(
      clk   => clk,
      rst_n => rst_n,
      en    => en,
      load  => load_sel,
      seed  => seed_sel,
      q     => sel_q_s,
      bit_o => sel_bit
    );

  -- 32-bit data
  u_dat: entity work.lfsr32
    port map(
      clk   => clk,
      rst_n => rst_n,
      en    => en,
      load  => load_dat,
      seed  => seed_dat,
      q     => dat_q_s,
      bit_o => dat_bit
    );

  -- Shrinking rule
  bit_o   <= dat_bit when sel_bit = '1' else '0';
  valid_o <= sel_bit;

  sel_q <= sel_q_s;
  dat_q <= dat_q_s;
end architecture;
